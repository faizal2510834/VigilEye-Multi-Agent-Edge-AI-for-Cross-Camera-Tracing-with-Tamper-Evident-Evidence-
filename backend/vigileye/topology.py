from config import TOPOLOGY

def get_neighbors(camera_id):
    """Return dict of neighbor_id: {mean, std} transit times."""
    return TOPOLOGY.get(camera_id, {})

def get_arrival_window(exit_time, mean_transit, std_transit, z_score=2.0):
    """
    Returns (min_time, max_time) for expected arrival.
    z_score = 2.0 covers ~95% of expected arrivals if normally distributed.
    """
    min_time = exit_time + mean_transit - (z_score * std_transit)
    max_time = exit_time + mean_transit + (z_score * std_transit)
    return min_time, max_time

def update_prior(camera_from, camera_to, actual_transit_time):
    """
    Online update of mean and std. In a real app this would persist.
    """
    if camera_from in TOPOLOGY and camera_to in TOPOLOGY[camera_from]:
        old_mean = TOPOLOGY[camera_from][camera_to]["mean"]
        # Simplified running average update for demo purposes
        new_mean = old_mean * 0.9 + actual_transit_time * 0.1
        TOPOLOGY[camera_from][camera_to]["mean"] = new_mean
        
        # Variance update simplified
        old_std = TOPOLOGY[camera_from][camera_to]["std"]
        diff = abs(actual_transit_time - new_mean)
        new_std = old_std * 0.9 + diff * 0.1
        TOPOLOGY[camera_from][camera_to]["std"] = max(1.0, new_std)
