import cv2
import torch
import numpy as np
import json
import os
import shutil
from ultralytics import YOLO
import open_clip
from PIL import Image
from collections import defaultdict

def blur_face(crop_img):
    """Blurs the top 25% of the image (approximate face region). Must work on a COPY."""
    h, w = crop_img.shape[:2]
    face_h = int(h * 0.25)
    result = crop_img.copy()
    if face_h > 0 and w > 0:
        face_region = result[:face_h, :]
        ksize = face_h if face_h % 2 != 0 else face_h - 1
        if ksize < 3: ksize = 3
        blurred = cv2.GaussianBlur(face_region, (ksize, ksize), 0)
        result[:face_h, :] = blurred
    return result

def variance_of_laplacian(image):
    return cv2.Laplacian(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()

def get_hsv_histogram(crop_img):
    """Extract HSV histogram from torso and legs (bottom 75%)"""
    h, w = crop_img.shape[:2]
    body = crop_img[int(h*0.25):, :]
    if body.size == 0:
        return np.zeros(512)
    hsv = cv2.cvtColor(body, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [16, 32], [0, 180, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()

def main():
    print("Loading YOLOv8n and OpenCLIP models...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    yolo = YOLO('yolov8n.pt')
    clip_model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai', device=device)
    
    video_path = os.path.join("data", "videos", "pedestrians.mp4")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0: fps = 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    print(f"Video Stats: FPS: {fps:.2f}, Total Frames: {total_frames}, Duration: {duration:.2f}s")
    
    seg_length = duration / 3.0
    cam_segments = [
        {"id": "cam_1", "start": 0, "end": seg_length},
        {"id": "cam_2", "start": seg_length, "end": seg_length*2},
        {"id": "cam_3", "start": seg_length*2, "end": duration + 1}, # +1 to catch last frames
    ]

    print("Segment boundaries:")
    for seg in cam_segments:
        print(f"  {seg['id']}: {seg['start']:.2f}s - {seg['end']:.2f}s")

    os.makedirs(os.path.join("data", "cache", "crops"), exist_ok=True)
    debug_dir = os.path.join("data", "cache", "debug_crops")
    if os.path.exists(debug_dir):
        shutil.rmtree(debug_dir)
    os.makedirs(debug_dir, exist_ok=True)
    os.makedirs("benchmarks", exist_ok=True)
    
    # Tracking data
    tracks_data = {}  # {cam_id: {track_id: {"class": cls, "crops": [], "timestamps": []}}}
    for seg in cam_segments:
        tracks_data[seg["id"]] = {}

    # Diagnostics
    frames_read = 0
    raw_detections = defaultdict(int)
    unique_track_ids_pre = set()
    survived_size = 0
    
    saved_debug_crops = 0

    print("Processing video frames sequentially...")
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frames_read += 1
        t = frame_idx / fps
        
        current_cam = None
        for seg in cam_segments:
            if seg["start"] <= t < seg["end"]:
                current_cam = seg["id"]
                break
                
        if current_cam is None:
            frame_idx += 1
            continue

        # Run tracking on EVERY frame
        results = yolo.track(frame, persist=True, tracker="bytetrack.yaml", classes=[0,2,3,5,7], verbose=False)
        
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            ids = results[0].boxes.id.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy()
            
            for box, track_id, cls in zip(boxes, ids, classes):
                raw_detections[int(cls)] += 1
                unique_track_ids_pre.add(int(track_id))
                
                x1, y1, x2, y2 = map(int, box)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                
                if x2 - x1 < 32 or y2 - y1 < 64:
                    continue
                    
                survived_size += 1
                crop = frame[y1:y2, x1:x2].copy()
                
                if int(cls) == 0:
                    crop = blur_face(crop)
                
                if saved_debug_crops < 5 and int(cls) == 0:
                    cv2.imwrite(os.path.join(debug_dir, f"debug_{saved_debug_crops}.jpg"), crop)
                    saved_debug_crops += 1
                
                tid_str = f"{current_cam}_{int(track_id)}"
                if tid_str not in tracks_data[current_cam]:
                    tracks_data[current_cam][tid_str] = {"class": int(cls), "global_id": int(track_id), "crops": [], "timestamps": []}
                    
                sharpness = variance_of_laplacian(crop)
                tracks_data[current_cam][tid_str]["crops"].append((sharpness, crop))
                tracks_data[current_cam][tid_str]["timestamps"].append(t)
                
        frame_idx += 1

    cap.release()
    print(f"\n--- Diagnostics ---")
    print(f"Frames read: {frames_read}")
    print(f"Raw detections per class: {dict(raw_detections)}")
    print(f"Unique Track IDs (pre-filter): {len(unique_track_ids_pre)}")
    print(f"Crops surviving size filter: {survived_size}")

    print("\nExtracting ReID embeddings...")

    # We will build embeddings for ALL crops first to do the train/test split per track
    track_embeddings = {} # global_id -> {"early": [], "late": []}
    final_db = []
    
    all_raw_embeddings = [] # to mean-centre
    extracted_features = [] # temp storage before centring
    
    survived_sharpness = 0
    
    for cam_id, tracks in tracks_data.items():
        for tid_str, data in tracks.items():
            if len(data["crops"]) < 2: continue # need at least 2 for early/late split
            
            # Sort by time
            time_sorted = sorted(zip(data["timestamps"], data["crops"]))
            
            # Subsample to a max of 10 for speed, keeping time order
            if len(time_sorted) > 10:
                step = len(time_sorted) / 10.0
                time_sorted = [time_sorted[int(i*step)] for i in range(10)]
                
            survived_sharpness += len(time_sorted)
            
            for t, (sharpness, crop) in time_sorted:
                img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
                t_img = preprocess(img).unsqueeze(0).to(device)
                
                with torch.no_grad():
                    clip_emb = clip_model.encode_image(t_img).cpu().numpy().flatten()
                
                hsv_hist = get_hsv_histogram(crop)
                
                extracted_features.append({
                    "cam_id": cam_id,
                    "tid_str": tid_str,
                    "global_id": data["global_id"],
                    "class": data["class"],
                    "t": t,
                    "clip": clip_emb,
                    "hsv": hsv_hist,
                    "crop": crop
                })
                all_raw_embeddings.append(clip_emb)

    print(f"Crops processed for embedding (after min 2 per track): {survived_sharpness}")
    if len(extracted_features) == 0:
        print("ERROR: No tracks survived filtering! Dataset too small/low res.")
        return

    # Mean center the clip embeddings
    mean_emb = np.mean(all_raw_embeddings, axis=0)
    
    # Process features
    track_splits = defaultdict(lambda: {"early": [], "late": []})
    
    # Group by tid_str to do early/late split per segment
    features_by_tid = defaultdict(list)
    for feat in extracted_features:
        features_by_tid[feat["tid_str"]].append(feat)
        
    for tid_str, feats in features_by_tid.items():
        feats.sort(key=lambda x: x["t"])
        mid = len(feats) // 2
        early_feats = feats[:mid]
        late_feats = feats[mid:]
        
        for split_feats, split_name in [(early_feats, "early"), (late_feats, "late")]:
            if not split_feats: continue
            
            fused_embs = []
            for f in split_feats:
                centered = f["clip"] - mean_emb
                normed_clip = centered / (np.linalg.norm(centered) + 1e-8)
                fused = np.concatenate([normed_clip, f["hsv"] * 0.2])
                fused = fused / (np.linalg.norm(fused) + 1e-8)
                fused_embs.append(fused)
            
            avg_fused = np.mean(fused_embs, axis=0)
            avg_fused = avg_fused / (np.linalg.norm(avg_fused) + 1e-8)
            
            gid = feats[0]["global_id"]
            track_splits[gid][split_name].append({
                "cam_id": feats[0]["cam_id"],
                "tid_str": f"{tid_str}_{split_name}",
                "emb": avg_fused,
                "class": feats[0]["class"],
                "timestamps": [f["t"] for f in split_feats],
                "crop": split_feats[0]["crop"]
            })

    # Evaluate Separability
    same_sims = []
    diff_sims = []
    gids = list(track_splits.keys())
    
    rank1_hits = 0
    rank1_total = 0
    
    for i, gid in enumerate(gids):
        splits = track_splits[gid]
        if not splits["early"] or not splits["late"]:
            continue
            
        early = splits["early"][0]
        late = splits["late"][0]
        
        same_sim = np.dot(early["emb"], late["emb"])
        same_sims.append(same_sim)
        
        # Rank-1 Hit Rate calculation
        best_sim = -1
        best_match_gid = None
        
        for j, other_gid in enumerate(gids):
            other_splits = track_splits[other_gid]
            if not other_splits["late"]: continue
            
            sim = np.dot(early["emb"], other_splits["late"][0]["emb"])
            if i != j:
                diff_sims.append(sim)
                
            if sim > best_sim:
                best_sim = sim
                best_match_gid = other_gid
                
        if best_match_gid == gid:
            rank1_hits += 1
        rank1_total += 1

    # Build final DB for backend
    for gid, splits in track_splits.items():
        for part in splits.values():
            for s in part:
                crop_path = f"data/cache/crops/{s['tid_str']}.jpg"
                cv2.imwrite(crop_path, s["crop"])
                
                final_db.append({
                    "camera_id": s["cam_id"],
                    "track_id": s["tid_str"],
                    "class": s["class"],
                    "first_ts": min(s["timestamps"]),
                    "last_ts": max(s["timestamps"]),
                    "dominant_color": "unknown",
                    "embedding": s["emb"].tolist(),
                    "crop_path": crop_path
                })

    # Save to JSON
    out_path = os.path.join("data", "cache", "tracks_db.json")
    with open(out_path, 'w') as f:
        json.dump(final_db, f)

    print(f"\nSaved {len(final_db)} real tracks to {out_path}.")
    
    # Print tracks per camera
    cam_counts = {}
    for t in final_db:
        cam_counts[t["camera_id"]] = cam_counts.get(t["camera_id"], 0) + 1
    print(f"Tracks per camera: {cam_counts}")

    # Cross-camera pairs
    cross_pairs = []
    for i in range(len(final_db)):
        for j in range(i+1, len(final_db)):
            t1 = final_db[i]
            t2 = final_db[j]
            sim = np.dot(t1["embedding"], t2["embedding"])
            if t1["camera_id"] != t2["camera_id"]:
                cross_pairs.append((sim, t1["track_id"], t2["track_id"]))
                
    cross_pairs.sort(reverse=True)
    top_10_cross = cross_pairs[:10]
    
    mean_same = np.mean(same_sims) if same_sims else 0
    std_same = np.std(same_sims) if same_sims else 0
    mean_diff = np.mean(diff_sims) if diff_sims else 0
    std_diff = np.std(diff_sims) if diff_sims else 0
    rank1 = (rank1_hits / rank1_total) if rank1_total > 0 else 0
    
    print(f"\n--- Separability Evaluation ---")
    print(f"Same-track Sim: {mean_same:.4f} +- {std_same:.4f}")
    print(f"Diff-track Sim: {mean_diff:.4f} +- {std_diff:.4f}")
    print(f"Rank-1 Hit Rate: {rank1*100:.1f}% ({rank1_hits}/{rank1_total})")
    
    print("\nTop 10 cross-camera pairs:")
    for sim, tr1, tr2 in top_10_cross:
        print(f"  {tr1} - {tr2}: {sim:.4f}")

    stats = {
        "tracks_per_camera": cam_counts,
        "separability": {
            "mean_same": float(mean_same),
            "std_same": float(std_same),
            "mean_diff": float(mean_diff),
            "std_diff": float(std_diff),
            "rank1_hit_rate": float(rank1)
        },
        "top_10_cross_camera_pairs": [{"pair": [tr1, tr2], "similarity": float(sim)} for sim, tr1, tr2 in top_10_cross]
    }
    
    with open("benchmarks/perception_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

if __name__ == "__main__":
    main()
