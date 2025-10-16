HOME_CITY  = "Columbia"
HOME_STATE = "Mo"      # adjust to your canonical format
HOME_VENUES = {"Taylor Stadium", "Taylor Stadium at Simmons Field"}

def _infer_location(venue_name, venue_city, venue_state):
    vn = (venue_name or "").lower()
    if any(hv.lower() in vn for hv in HOME_VENUES):
        return "home"
    if (venue_city or "").strip().lower() == HOME_CITY.lower():
        return "home"
    # If you later detect explicit “Neutral” in the card, return "neutral" here.
    if venue_city or venue_state or venue_name:
        return "away"
    return None