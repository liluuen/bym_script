#! /usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import re
import hashlib


#LOG IN

username = 'username'
password = 'password'
replace_text = '--'

md5pwd = hashlib.md5(password.encode()).hexdigest()

m = hashlib.md5()
m.update(password.encode('utf-8'))
md5pwsutf = m.hexdigest()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0'
}

params = (
    ('do', 'login'),
)

data = {
  'vb_login_username': username,
  'vb_login_password': '',
  'vb_login_password_hint': 'Kennwort',
  's': '',
  'securitytoken': 'guest',
  'do': 'login',
  'vb_login_md5password': md5pwd,
  'vb_login_md5password_utf': md5pwsutf
}

response = requests.get('https://www.bym.de/forum/login.php', headers=headers, params=params, data=data)

cookies = response.cookies.get_dict()

response = requests.get('https://www.bym.de/forum', headers=headers, cookies=cookies)

user_id = re.search('profil\/(\d+)', response.text).group(1)
search_id = re.search('searchid=(\d+)', response.text).group(1)
security_token = response.text.split('SECURITYTOKEN = "')[1].split('"')[0]

params = (
    ('do', 'process'),
)

data = [
  ('query', ''),
  ('titleonly', '0'),
  ('searchuser', username),
  ('starteronly', '0'),
  ('exactname', '1'),
  ('tag', ''),
  ('childforums', '1'),
  ('replyless', '0'),
  ('replylimit', ''),
  ('searchdate', '0'),
  ('beforeafter', 'after'),
  ('sortby', 'dateline'),
  ('order', 'descending'),
  ('showposts', '1'),
  ('dosearch', 'Suchen'),
  ('searchthreadid', ''),
  ('s', ''),
  ('securitytoken', security_token),
  ('searchfromtype', 'vBForum:Post'),
  ('do', 'process'),
  ('contenttypeid', '1'),
]

response = requests.post('https://www.bym.de/forum/search.php', headers=headers, params=params, cookies=cookies, data=data)


#EXTRACT IDS

list_of_lists = []

for page in range(1, 100):

    params = (
        ('searchid', search_id),
        ('pp', ''),
        ('page', str(page)),
        )   
    
    response = requests.get('https://www.bym.de/forum/search.php', headers=headers, params=params, cookies=cookies)

    soup = BeautifulSoup(response.text, "html.parser")
    selector = 'div > h3 > a'
    hrefs = soup.select(selector)
    post_ids = [href['href'][-10:] for href in hrefs]
    list_of_lists.append(post_ids)
    
all_ids = [item for sublist in list_of_lists for item in sublist]

print("There are {} posts to delete.".format(len(all_ids)))
print("Test:" + all_ids[0])


#SAVE POSTS
#create a .txt-file, insert your own file path

for i in all_ids:
    text = soup.find('div', id='post_message_' + str(i))
    with open(r"C:\Users\Anwender\Desktop\bym\bymmel.txt", "a") as file:
      file.write(str(text.text))
      

#NUKE POSTS!

to_edit = []

for i in all_ids:
	
	data = {
		'do': 'deletepost',
		's': '',
		'securitytoken': security_token,
		'postid': i,
		'deletepost': 'delete',
		'reason': ''
		}

	response = requests.post('https://www.bym.de/forum/editpost.php', headers=headers, cookies=cookies, data=data)
	
	if "Du hast keine Rechte" in response.text:
		to_edit.append(i)
		print(str(i)+" can not be deleted.")


#EDIT THREADS

for ids in to_edit:

    params = (
        ('do', 'updatepost'),
        ('p', ids),
        )

    data = {
        'reason': '',
        'title': '',
        'message_backup': '-',
        'message': replace_text,
        's': '',
        'securitytoken': security_token,
        'do': 'updatepost',
        'p': ids,
        }

    response = requests.post('https://www.bym.de/forum/editpost.php', headers=headers, params=params, cookies=cookies, data=data)


print("Done!")
