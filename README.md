# maoyan_font_decryption
Comprehensive font decryption schema written in python
Recently, the font encryption technique is quite popularity used for Chinese sites, for prevent data scraping, the senstive data such as the numbers is encoded
using a special method - Font encryption, below is an example on maoyan.com (a popular movie site in Chinese)
![Maoyan.com - Font encryption](maoyan_font_screenshot.png)

Obviously, the numbers from HTML Source is encoded as HTML entities (unicode text), even you decode the HTML entities as unicode text, it's still messing unicode chars not the actual numbers as you desired.
```
<span class="index-left info-num one-line"><span class="stonefont">&#xea90;&#xe607;&#xe94e;&#xea90;&#xf351;</span></span>
```

# Major module - !(font_decrypt.py)[font_decrypt.py]
It is the major module to decrypt the numbers encrypted in Font. 
In general, you might just use the two functions to decrypt the numbers :
## decryptHtmlNumbers
Parameter -'s' is the original HTML entity text that looks like 
&amp;#xF09F;&amp;#xE690;&amp;#xEA64;&amp;#xF031;&amp;#xE238;&amp#xF031;
&amp;#xE238;.&amp#xF031;
**Note**, the 'dot' char is allowed.
Parameter - 'font' can be either url or local font file path, it does recognize the difference if 'http://' or 'https://' is leading of the parameter.

## decryptRawNumbers
Same usage as decryptHtmlNumbers, but the parameter - 's' should be raw unicode text
