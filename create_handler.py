from threading import Timer


def create_matrix(wells):
    # create a matrix of 0 values
    matrix = []
    for box in wells:
        matrix.append([])
        for row in box:
            matrix[-1].append([])
            for well in row:
                matrix[-1][-1].append(0)
    return matrix


def create_handler(wells, tracks):
    matrix = create_matrix(wells)
    t = None

    def flush():
        nonlocal matrix
        nonlocal tracks
        matrix = create_matrix(wells)
        # remove all array items without reassignment
        del tracks[:]
        start_timer()

    def start_timer():
        nonlocal t
        t = Timer(5, flush)
        t.start()

    def cancel_timer():
        nonlocal t
        if t is not None:
            t.cancel()

    start_timer()

    def handler(e):
        box, row, col, distance = e.box, e.row, e.well, e.distance
        matrix[box][row][col] += distance
        center = tuple(e.contour[0][0])
        tracks.append(center)

    return handler, cancel_timer
