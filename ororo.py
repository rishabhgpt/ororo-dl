import sys, urllib2, pycurl
from bs4 import BeautifulSoup as BS


def download_me(url):
	file_name = url.split('/')[-1]
	# Get args
	num_conn = 10
	urls=[]
	try:
		if sys.argv[1] == "-":
		    urls = sys.stdin.readlines()
		else:
		    urls.append(url)
		if len(sys.argv) >= 3:
		    num_conn = int(sys.argv[2])
	except:
		print("Usage: %s <file with URLs to fetch> [<# of concurrent connections>]" % sys.argv[0])
		raise SystemExit


	# Make a queue with (url, filename) tuples
	queue = []
	for url in urls:
		url = url.strip()
		if not url or url[0] == "#":
		    continue
		filename = "doc_%03d.dat" % (len(queue) + 1)
		queue.append((url, filename))


	# Check args
	assert queue, "no URLs given"
	num_urls = len(queue)
	num_conn = min(num_conn, num_urls)
	assert 1 <= num_conn <= 10000, "invalid number of concurrent connections"
	print("PycURL %s (compiled against 0x%x)" % (pycurl.version, pycurl.COMPILE_LIBCURL_VERSION_NUM))
	print("----- Getting", num_urls, "URLs using", num_conn, "connections -----")


	# Pre-allocate a list of curl objects
	m = pycurl.CurlMulti()
	m.handles = []
	for i in range(num_conn):
		c = pycurl.Curl()
		c.fp = None
		c.setopt(pycurl.FOLLOWLOCATION, 1)
		c.setopt(pycurl.MAXREDIRS, 5)
		c.setopt(pycurl.CONNECTTIMEOUT, 30)
		c.setopt(pycurl.TIMEOUT, 300)
		c.setopt(pycurl.NOSIGNAL, 1)
		c.setopt(pycurl.HTTPHEADER,['User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36','Cookie:video=true;_ga=GA1.2.339709105.1424606219;_ororo_session=RlVKU2JUYWkyUzIvQUJGMTMxZ0JKcExzM2pxSWdzcEdCWEw3RlNDbmh5UkpaeDFqeC9jR1Y1WGNJSHgzazVhLzJFaGNLOG4wR0hsdlBHcGtQZjBhTHY3ZHB1WVdralB5UjdzNFdJQVlmdU5lcG4xN2dLT3c2WTNvRFpNNWtaMGRsV2V2enFXT0hqZTBoNzJPV3JiaGNMWHFOcFUzVmV6VkthQTlGaFEzYlFLeDg3bG8wZWxydTF4eHBnY1Z5VmF1a1VsNVJsQU9ySlhMYTNXR1VGNzREZmV6aURUMzBPeXRTWENBM2psM0dzcz0tLXc0VjlBZjUrV3hlSTUxSTRDTEk0RHc9PQ%3D%3D--c030986d158d66528261ff4297006f14e1fc0d87'])
		m.handles.append(c)


	# Main loop
	freelist = m.handles[:]
	num_processed = 0
	while num_processed < num_urls:
		# If there is an url to process and a free curl object, add to multi stack
		while queue and freelist:
		    url, filename = queue.pop(0)
		    c = freelist.pop()
		    c.fp = open(filename, "wb")
		    c.setopt(pycurl.URL, url)
		    c.setopt(pycurl.WRITEDATA, c.fp)
		    m.add_handle(c)
		    # store some info
		    c.filename = filename
		    c.url = url
		# Run the internal curl state machine for the multi stack
		while 1:
		    ret, num_handles = m.perform()
		    if ret != pycurl.E_CALL_MULTI_PERFORM:
		        break
		# Check for curl objects which have terminated, and add them to the freelist
		while 1:
		    num_q, ok_list, err_list = m.info_read()
		    for c in ok_list:
		        c.fp.close()
		        c.fp = None
		        m.remove_handle(c)
		        print("Success:", c.filename, c.url, c.getinfo(pycurl.EFFECTIVE_URL))
		        freelist.append(c)
		    for c, errno, errmsg in err_list:
		        c.fp.close()
		        c.fp = None
		        m.remove_handle(c)
		        print("Failed: ", c.filename, c.url, errno, errmsg)
		        freelist.append(c)
		    num_processed = num_processed + len(ok_list) + len(err_list)
		    if num_q == 0:
		        break
		# Currently no more I/O is pending, could do something in the meantime
		# (display a progress bar, etc.).
		# We just call select() to sleep until some more data is available.
		m.select(1.0)


	# Cleanup
	for c in m.handles:
		if c.fp is not None:
		    c.fp.close()
		    c.fp = None
		c.close()
	m.close()
	

def main():

	if len(sys.argv)<3:
		print "Run like python ororo.py <series-name> <season> <episode>\nExample:\tpython ororo.py arrow 1 10"
		print "If whole season is to be downloaded then run link 'python ororo.py <series-name> <season> all'"
		exit()
	_series=sys.argv[1]
	_season=sys.argv[2]
	_episode=sys.argv[3]
	print _series+" "+_season
	html_content=urllib2.urlopen('http://ororo.tv/en/shows/'+_series+'#'+_season).read()

	soup=BS(html_content)
	links=soup.find_all("a",attrs={"class":"episode"})
	print "List of Episodes\n"
	for episode in links:
		epi=(episode.get('href'))
		season=epi.split("-")[0][1:]
		if season==_season:
			print episode.text
	for episode in links:
		epi=(episode.get('href'))
		season=epi.split("-")[0][1:]
		episodee=epi.split("-")[1]
		if season==_season:
			link=(episode.get('data-href'))
			link='http://ororo.tv'+link
			html_content=urllib2.urlopen(link).read()
			soup=BS(html_content)
			dl_link=soup.find('source')
			dl_link=dl_link.get('src')
			subs_link=soup.find_all("track",attrs={"label":"en"})
			subs_link='http://ororo.tv'+subs_link[0].get('src')
			print dl_link
			print subs_link
			print _episode
			if episodee==_episode:
				download_me(subs_link)
				download_me(dl_link)
				break;
			elif _episode=="all":
				download_me(subs_link)
				download_me(dl_link)
						
if __name__=="__main__":
	main()	
