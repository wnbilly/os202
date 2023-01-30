from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    token = 1
    comm.send(token, dest=1)
    token = comm.recv(source = size - 1)
    print("Token received by 0, value :", token)
elif 0 < rank < size - 1:
    token = comm.recv(source = rank - 1)
    comm.send(token+1, dest = rank + 1)
elif rank == size - 1:
    token = comm.recv(source = rank - 1)
    comm.send(token, dest = 0)