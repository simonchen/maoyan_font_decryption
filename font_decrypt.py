# -*- coding: utf-8 -*-
# maoyan font decryption

import os, sys
import six, math, traceback
import string
try:
    from urllib2 import Request, urlopen
except:
    from urllib.request import Request, urlopen # Python 3
try:
    from urllib2 import HTTPError, URLError
except:
    from urllib.error import HTTPError, URLError # Python 3
try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode # Python 3

try:
    from fontTools.ttLib import TTFont
except Exception as e:
    pass

try:
    cur_filepath = __file__
except NameError:  # We are the main py2exe script, not a module
    import sys
    cur_filepath = os.path.abspath(sys.argv[0])
cur_dir = os.path.dirname(os.path.abspath(cur_filepath))
_standard_font_file = r"%s\8e0fa582edd4bbe2bfbe60ba6ee48c9e2276.woff" %cur_dir # standard font
#print _standard_font_file
_compare_font_file = r"C:\Users\Chen\Downloads\0a56a723d694fa7d1caf5001dbc95c5f2288.woff" # for comparison
_standard_cmap = {
    'F3A8': 0,
    'F4A8': 1,
    'F6FA': 2,
    'F7B6': 3,
    'E39C': 4,
    'E0DB': 5,
    'EC74': 6,
    'EC5A': 7,
    'EFAE': 8,
    'ED06': 9,
}

def _getGlyphCoordinates(filepath):
    """
    Getting font contours saving in dictionary
    """
    font = TTFont(filepath)
    # font.saveXML("bd10f635.xml")
    glyfList = list(font['glyf'].keys())
    data = dict()
    for key in glyfList:
        if key[0:3] == 'uni':
            coords = font['glyf'][key].coordinates
            flags = font['glyf'][key].flags
            #print flags
            data[key.replace('uni', '')] = [(tup[0], tup[1], flags[i]) for i, tup in enumerate(coords)]
    return data

def _get_curves(c):
    return sum([1 if flag == 0 else 0 for x, y, flag in c])

def _comp_curves(c1, c2):
    c1_curves = sum([1 if flag == 0 else 0 for x, y, flag in c1])
    c2_curves = sum([1 if flag == 0 else 0 for x, y, flag in c2])
    return (c1_curves == c2_curves)

### HTML DECODER ################
def _html_numbers_decode(orig_str):
    s = u''
    hex_list = []
    section_list = orig_str.replace("&#x", "").split('.') # see if numbers would be splitted by dot?
    if len(section_list) > 1:
        for i, section in enumerate(section_list):
            section = section.strip(';')
            hex_list.extend([six.unichr(int(hex_chars, 16)) for hex_chars in section.split(';')])
            if i < (len(section_list)-1):
                hex_list.extend(u'.')
        #print hex_list
        s = ''.join(hex_list)
    else:
        hex_list = section_list[0].strip(';').split(';')
        s = ''.join([six.unichr(int(hex_chars, 16)) for hex_chars in hex_list])

    return s

#print _html_numbers_decode('&#xF09F;&#xE690;&#xEA64;&#xF031;&#xE238;.&#xF031;').encode('utf-8')
#sys.exit(0)
#################################

def getUrlMap(font_url):
    """ Getting char mapping table from font_url """

    try:
        resp = urlopen(font_url)
        raw_font_stream = six.BytesIO(resp.read())
        resp.close()
    except:
        return {}

    return getStreamMap(raw_font_stream)

def getStreamMap(raw_font_stream):
    """ Geting char mapping table from font stream """
    std_coords = _getGlyphCoordinates(_standard_font_file)
    #print std_coords['ED06']
    comp_coords = _getGlyphCoordinates(raw_font_stream)
    #print comp_coords
    #return
    #print comp_coords['F119'] #['EB00']
    #print comp_curves(std_coords['E0DB'], comp_coords['EB00'])
    cmap = {'2E': '.'} # dot

    for std_uni, std_points in std_coords.items():
        std_pt= [math.sqrt(item[0]**2+item[1]**2) for item in std_points]
        std_num = _standard_cmap[std_uni]
        std_var = getVar(std_pt)
        #print 'Number=%s, looking on glyphs' %num
        curves_matches = []
        gen_matches = []
        for comp_uni, comp_points in comp_coords.items():
            comp_pt = [math.sqrt(item[0]**2+item[1]**2) for item in comp_points]
            pt_divs = []
            same_pt_cnt = 0
            for i, pt in enumerate(std_pt):
                if i > (len(comp_pt)-1): break
                # find the closest point the make division
                try:
                    comp_pt.sort(lambda p1, p2: 1 if abs(p1-pt) > abs(p2-pt) else -1)
                except:
                    comp_pt.sort(key=lambda k: abs(k-pt), reverse=False)
                pt_divs.append(pt / comp_pt[0])
                if (pt == comp_pt[0]): same_pt_cnt += 1
            ##if std_num == 9:
            ##    print comp_uni, getVar(pt_divs), abs(len(comp_points)-len(std_points)), same_pt_cnt
            #if std_num == 3:
            #    score = getVar(pt_divs)
            #else:
            std_pt_num = len(std_points)
            comp_pt_num = len(comp_points)
            score = getVar(pt_divs) * (std_pt_num-min(std_pt_num,same_pt_cnt*(0.25*std_pt_num)))/std_pt_num * max(1, abs(std_pt_num-comp_pt_num)) # important formula to score the similarity
            if _comp_curves(std_points, comp_points) or score < 10:
                #if std_num == 3: print (comp_uni, score, abs(len(comp_points)-len(std_points)))
                curves_matches.append((comp_uni, score))
            gen_matches.append((comp_uni, score))
        if len(curves_matches) == 0:
            curves_matches = gen_matches
        try:
            curves_matches.sort(lambda m1, m2: 1 if m1[1] > m2[1] else -1)
        except:
            curves_matches.sort(key=lambda k: k[1], reverse=False)
        if len(curves_matches) > 0:
            #print std_num, curves_matches
            cmap[curves_matches[0][0]] = std_num

    #print cmap
    return cmap

def decryptRawNumbers(s, font):
    """ Parameter - font can be either
        ~ URI starting with http:// or https://
        ~ Font file stream as byte type
    """
    ret = []
    ##print repr(type(s) is unicode)
    #if type(s) is not unicode:
    #    try:
    #        s = unicode(s, 'utf8')
    #    except:
    #        return ret
    if font.startswith('http'):
        cmap = getUrlMap(font)
    else:
        try:
            f = open(font, 'rb')
            cmap = getStreamMap(f.read())
            f.close()
        except:
            cmap = getStreamMap(font)
    ##print cmap
    for c in s:
        hexstr = hex(ord(c)).replace('0x', '').upper()
        #print hexstr
        ret.append(cmap.get(hexstr))

    return ''.join([str(n) for n in ret])

def decryptHtmlNumbers(html_numbers, font):
    s = _html_numbers_decode(html_numbers)
    return decryptRawNumbers(s, font)

def getVar(results):
    # https://stackoverflow.com/questions/35583302/how-can-i-calculate-the-variance-of-a-list-in-python/35583512
    # calculate mean
    m = sum(results) / len(results)

    # calculate variance using a list comprehension
    var_res = sum((xi - m) ** 2 for xi in results) / len(results)

    return var_res

def test_fixed_urls():
    trianing_samples = [{
        "font_url": "http://vfile.meituan.net/colorstone/83fbe7baa38e1e3d48ca10516adc6e232276.woff",
        "s": u'\ueb00\ue993\ue4dc\uf492\uf63c',
        "n": 13905
    }, {
        "font_url": "http://vfile.meituan.net/colorstone/9fbe7b0601dcf9cb0e8d37713f54d71e2268.woff",
        "s": u'\uF180\uF7C6\uE03C\uEF5C\uF094',
        "n": 14320
    }, {
        "font_url": "http://vfile.meituan.net/colorstone/541402d9c3ebc21cb1b0ba87bb2689e12272.woff",
        "s": u'\uE060\u002E\uE8FE',
        "n": 6.8
    }, {
        "font_url": "http://vfile.meituan.net/colorstone/ea6a3454b315b221d92c65af2b40bae52284.woff",
        "s": u'\uEB32\uE2C5\uF381\uF6A9\uF6A9',
        "n": 70922
    }, {
        "font_url": "http://vfile.meituan.net/colorstone/853b5f061e251cc12982e6da8cc636f22276.woff",
        "s": u'\uE307\uE1E3\uE7A4\uE196',
        "n": 7031
    }, {
        "font_url": "http://vfile.meituan.net/colorstone/ed7a60986760fc0b48e7f139104610112276.woff",
        "s": u"\uea69\ue2b4\ueff2\uf443\ue610\uea69\uefc1",
        "n": 2307629
    }]

    #trianing_samples = [trianing_samples[3]]

    for ts in trianing_samples:
        font_url = ts['font_url']
        s = ts['s']
        n = ts['n']
        ret = decryptRawNumbers(s, font_url)
        print '>>> Decrypted numbers=%s, Actual numbers=%s' %(ret, n)

def test_maoyan(url):
    # movie url
    #url = "https://maoyan.com/films/1217024"
    from cookielib import CookieJar
    cookie = '__mta=213670571.1594194939580.1594606677853.1594606681346.21; uuid_n_v=v1; uuid=681D5BE0C0F011EAB2AE8B45D9A9C865E326C0AA8CCC4AB5A05AFCE71BC8AEEA; _lxsdk_cuid=1732d6c4e6ec8-0aa6b27b9b70ff-4353760-1fa400-1732d6c4e6e4d; _lxsdk=681D5BE0C0F011EAB2AE8B45D9A9C865E326C0AA8CCC4AB5A05AFCE71BC8AEEA; mojo-uuid=305f4ee2902d0c0c7c84f4c032b8ec27; _csrf=4cb33b2c2eca4cfb4eb016c6e41f9798a108f0603364bd3c761be637360a9573; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1594194939,1594347741; mojo-session-id={"id":"fadc38343da357dd413cb268d51d07e4","time":1594604586599}; __mta=213670571.1594194939580.1594477814934.1594605108799.14; mojo-trace-id=12; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1594606681; _lxsdk_s=17345d6d77c-b82-cd7-2e9%7C%7C18'
    req = Request(url, headers={'Cookie': cookie, 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'})
    resp = urlopen(req)
    html = resp.read()
    resp.close()

    font_url, s = None, None
    import re
    ret = re.findall("url\('([^']+)'\) format\('woff'\)", html, re.IGNORECASE)
    if ret:
        font_url = "http:" + ret[0]
        #print font_url
    #print html
    #print html.find('stonefont')
    ret = re.findall(r"<span class=\"stonefont\">([^<>]+)</span>", html, re.IGNORECASE)
    #print ret
    if ret:
        orig_str = ret[0]
        print orig_str
        s = _html_numbers_decode(orig_str)
        #print s
    if font_url and s:
        ret = decryptRawNumbers(s, font_url)
        print '>>> Encrypted: font_url=%s, s=%s,\r\n>>> Decrypted numbers=%s' %(font_url, orig_str, ret)

if __name__ == '__main__':
    #print 'param len=%s' %len(sys.argv)
    if len(sys.argv) <= 1:
        print 'Usage: %s [-test ] | [-test_maoyan [url]] | [-d {html_numbers} {font_url|font_filepath}]' %os.path.basename(cur_filepath)
    else:
        if sys.argv[1] == '-test':
            try:
                test_fixed_urls()
            except:
                print traceback.print_exc()
        if sys.argv[1] == '-test_maoyan':
            if len(sys.argv) > 2:
                for i in range(0, eval(sys.argv[3])):
                    test_maoyan(url=sys.argv[2])
            else:
                test_maoyan(url=sys.argv[2])
        if sys.argv[1] == '-d':
            ret = decryptHtmlNumbers(sys.argv[2], sys.argv[3])
            print ret
    #print "ok"
