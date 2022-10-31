def zero_pad(num):
    if num < 10:
        return f"00{num}"
    elif num < 100:
        return f"0{num}"
    else:
        return num
