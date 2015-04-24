import os, sys, urllib2
from bs4 import BeautifulSoup as BS


def download_me(url):
	file_name = url.split('/')[-1]
	folder_name = sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]
	if not os.path.exists('./'+folder_name):
		os.mkdir('./'+folder_name)
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36')
	req.add_header('Cookie','video=true;_ga=GA1.2.339709105.1424606219;_ororo_session=RlVKU2JUYWkyUzIvQUJGMTMxZ0JkcExzM2pxSWdzcEdCWEw3RlNDbmh5UkpaeDFqeC9jR1Y1WGNJSHgzazVhLzJFaGNLOG4wR0hsdlBHcGtQZjBhTHY3ZHB1WVdralB5UjdzNFdJQVlmdU5lcG4xN2dLT3c2WTNvRFpNNWtaMGRsV2V2enFXT0hqZTBoNzJPV3JiaGNMWHFOcFUzVmV6VkthQTlGaFEzYlFLeDg3bG8wZWxydTF4eHBnY1Z5VmF1a1VsNVJsQU9ySlhMYTNXR1VGNzREZmV6aURUMzBPeXRTWENBM2psM0dzcz0tLXc0VjlBZjUrV3hlSTUxSTRDTEk0RHc9PQ%3D%3D--c030986d158d66528261ff4297006f14e1fc0d87')
	try:
		u = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		print e.fp.read()
	file_name='.'+os.path.sep+folder_name+os.path.sep+file_name
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s : %s KB" % (file_name, file_size/(1024))
	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
  		if not buffer:
  			break
  		file_size_dl += len(buffer)
  		f.write(buffer)
  		status = r"%10d  [%3.2f%%]" % (file_size_dl/(1024), file_size_dl * 100. / file_size)
  		status = status + chr(8)*(len(status)+1)
  		print status,
	f.close()

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
			try:
				subs_link='http://ororo.tv'+subs_link[0].get('src')
			except:
				pass
			print dl_link
			print subs_link
			print _episode
			if episodee==_episode:
				try:
					download_me(subs_link)
				except:
					pass
				download_me(dl_link)
				break;
			elif _episode=="all":
				try:
					download_me(subs_link)
				except:
					pass
				download_me(dl_link)
						
if __name__=="__main__":
	main()
