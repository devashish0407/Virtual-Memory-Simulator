def format_frames_state(frames_list):
    formatted_frames = []
    for i, vpn in enumerate(frames_list):
        if vpn is not None:
            formatted_frames.append(f"F{i}:VPN{vpn}")
        else:
            formatted_frames.append(f"F{i}:Empty")
    return " | ".join(formatted_frames)