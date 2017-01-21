import glob
import multiprocessing
import os
import requests
import urllib2

from BeautifulSoup import BeautifulSoup

from logger import logger

def get_script_url(link):
    """
    This function takes the link get the content
    from the url link and retrieves all the javascript
    script urls.
    args:
        link - Link of for the input url to be fetched
    return:
        returns the list of javascript urls
    """
    script_urls_list = []
    script_sources = []
    logger.info('Strart processing link %s', link)
    try:
        page = urllib2.urlopen(link)
        soup = BeautifulSoup(page.read())
        script_sources = soup.findAll('script', {"src":True})
    except:
        logger.error('Could not process the link %s', link)

    script_url_list = []
    for source in script_sources:
        script_url_list.append(source['src'])
    return script_url_list


def has_jquery_in_urls(script_url_list):
    """
    This function takes the list of script urls list
    and tris to find wether jquery.js is present in
    it.

    args:
        script_url_list: list of javascript url in the webpage.
    return:
        Boolean: True if jquery is present else False
    """

    jquery_js_str = 'jquery.js'

    for script_url in script_url_list:
        if jquery_js_str in script_url:
            return True
    return False


class LinkProcessor(object):
    """
    LinkProcessor class for
    managing temp file and proccessing
    links.
    """
    reject_temp_file = None
    accept_temp_file = None


    @staticmethod
    def set_accept_reject_temp_files():
        """
        This method open reject and accept link
        for the LinkProcessor.
        """
        process_pid = multiprocessing.current_process().pid
        temp_accept_file_name = '{0}-accept.temp'.format(process_pid)
        temp_reject_file_name = '{0}-reject.temp'.format(process_pid)
        # open accept temp file
        LinkProcessor.accept_temp_file = open('temp/' + temp_accept_file_name, 'a+')
        # open reject temp file
        LinkProcessor.reject_temp_file = open('temp/' + temp_reject_file_name, 'a+')


    @staticmethod
    def close_accept_reject_temp_files():
        """
        method to close accept reject temp files
        """
        print LinkProcessor.accept_temp_file
        if LinkProcessor.accept_temp_file is not None:
            logger.info('closing accept temp file')
            LinkProcessor.accept_temp_file.close()

        print LinkProcessor.reject_temp_file
        if LinkProcessor.reject_temp_file is not None:
            logger.info('closing reject temp file')
            LinkProcessor.reject_temp_file.close()


    @staticmethod
    def process_link(link):
        """
        This method takes link and processes it for jquery.js.
        if jquery.js is present it appends the url link to
        process_id-accept.temp else it appends the url to
        process-id-reject.temp file.

        Note: We are creating accept, reject  temp files because
        multiple processes in Pool will simultaneously write the
        result to their respective process-id temp files. If We
        started writing directly to accept and reject csv, then
        we have to handle(mutex - lock) on these files due to
        which performance will decrease significantly.

        args:
            link: Link to be processed.
        return:
            None
        """
        script_url_list = get_script_url(link)
        print script_url_list
        has_jquery_in_link = has_jquery_in_urls(script_url_list)
        if (LinkProcessor.reject_temp_file is None or
            LinkProcessor.accept_temp_file is None):
            LinkProcessor.set_accept_reject_temp_files()

        # writable link
        write_link = link + '\n'

        if has_jquery_in_link:
            logger.info("Writing %s link to accept temp file", link)
            LinkProcessor.accept_temp_file.write(write_link)
        else:
            logger.info("Writing %s link to reject temp file", link)
            LinkProcessor.reject_temp_file.write(write_link)


def merge_accept_reject_temp():
    """
    This function merges all the accept temp files and
    reject temp files to accept.txt and reject.txt
    respectively.
    """
    temp_dir_path = './temp'
    temp_file_names = [file for file in os.listdir(temp_dir_path)]
    # get all accept temp files
    accept_temp_file_names = filter(lambda f_name: 'accept' in f_name,
                                    temp_file_names)
    # get all reject temp files
    reject_temp_file_names = filter(lambda f_name: 'reject' in f_name,
                                    temp_file_names)
    # merged accept.txt file
    with open('accept.txt', 'w+') as outfile:
        for fname in accept_temp_file_names:
            with open('temp/'+ fname) as accept_temp_file:
                outfile.write(accept_temp_file.read())
                outfile.flush()


    # merged reject.txt file
    with open('reject.txt', 'w+') as outfile:
        for fname in reject_temp_file_names:
            with open('temp/'+ fname) as reject_temp_file:
                outfile.write(reject_temp_file.read())
                outfile.flush()

def delete_all_temp_files():
    """
    utility function to delete all temp files.
    """
    temp_files = glob.glob('temp/*')
    for temp_file in temp_files:
        os.remove(temp_file)

