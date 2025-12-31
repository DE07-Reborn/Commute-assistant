from datetime import timedelta

def calculate_depart_at(arrive_by, total_duration_sec, feedback_min):
    """
        Calculate adjust depart time with feedback
        param 
            arrive_by : Estimated time of arrive at work address from api
            total_duration_sec : Total seconds to go work address
            feedback_min : Individual's feedback on route
    """
    return arrive_by - timedelta(
        seconds=total_duration_sec + feedback_min * 60
    )

def adjust_route_for_display(route, feedback_min):
    """
        Adjust information of first Walk time with feedback minutes
        param
            route : route json from api
            feedback_min : Individual's feedback on route
    """
    if not route["segments"]:
        return route

    first = route["segments"][0]
    if first["type"] == "walk":
        first["duration_sec"] += feedback_min * 60

    return route