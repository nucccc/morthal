def max_and_avg(l: list[int]) -> tuple[int, float]:
    mx = 0
    sm = 0.0

    for elem in l:
        mx = max(elem, mx)
        sm += elem
    
    avg = sm / len(l)

    return mx, avg