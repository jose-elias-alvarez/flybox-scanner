import asyncio
import time


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
    # track last flush time for debugging
    last_flush = deadline = time.time()

    async def flush():
        nonlocal matrix, tracks
        matrix = create_matrix(wells)
        tracks.clear()
        now = time.time()
        nonlocal last_flush
        print(f"Flushed at {now - last_flush} seconds")
        last_flush = now

    async def start_timer():
        nonlocal deadline
        while True:
            deadline += 5
            now = time.time()
            sleep = max(0, deadline - now)
            await asyncio.sleep(sleep)
            await flush()

    asyncio.ensure_future(start_timer())

    def handler(e):
        box, row, col, distance = e.box, e.row, e.well, e.distance
        matrix[box][row][col] += distance
        center = tuple(e.contour[0][0])
        tracks.append(center)

    return handler
