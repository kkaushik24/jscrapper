import os
from multiprocessing import Pool, TimeoutError

from constants import CPU_CORES
from logger import logger
from utils import LinkProcessor
from utils import merge_accept_reject_temp, delete_all_temp_files


def process_wrapper1(chunk_start, chunk_size):
    """
    This function reads the urls file(which may
    contain million of row entries of urls) from
    chunk start to (chunk start + chunk size).
    Note: We are chunking the file during read to avoid
    main memory over flow.

    args:
        chunk_start: start point from where we want to
                     read the file.
        chunk_size: the amount of chunk we want want
                    to read.
    return: None
    """
    with open('urls.txt') as file:
        # seek to chunk start position
        file.seek(chunk_start)
        # get all the lines in chunk
        lines = file.read(chunk_size).splitlines()
        for line in lines:
            # start processing the line
            LinkProcessor.process_link(line)

    LinkProcessor.close_accept_reject_temp_files()


def chunkify(file_name, size=1024*1024):
    """
    This method is a generator which takes file and
    returns chunk start and chunk size at every yield.

    args:
        file_name: name of the file which we want
                   to chunkify.
        size: size of every chunk. By default it
              is 1024 * 1024
    """
    # get the file size as file end
    file_end = os.path.getsize(file_name)
    with open(file_name, 'r') as file:
        # set chunk end to current read/write pointer
        # of the file.
        chunk_end = file.tell()
        while True:
            # set chunk start position
            chunk_start = chunk_end
            # seek to chunk size
            file.seek(size, 1)
            file.readline()
            # set chunk end
            chunk_end = file.tell()
            # yield chunk_start and chunk_end
            yield chunk_start, chunk_end - chunk_start

            if chunk_end > file_end:
                break


def main():
    # create pool for parallel processing
    pool = Pool(CPU_CORES)
    # jobs that should be processed parallely
    jobs = []
    for chunk_start, chunk_size in chunkify('urls.txt'):
        # asynchronously call process_wrapper for processing.
        jobs.append(pool.apply_async(process_wrapper1,
                                     (chunk_start, chunk_size)))
    # get the result for the jobs.
    for job in jobs:
        try:
            # Note: We can set time out if process is taking too long
            # just change the below line to (job.get(timout=timeout)
            job.get()
        except TimeoutError:
            logger.error('Could not process the job in\
                         one second time frame')

    # clean up
    pool.close()

    # merge all temp files.
    merge_accept_reject_temp()

    # delete all the files in temp folder
    delete_all_temp_files()


if __name__ == "__main__":
    main()

