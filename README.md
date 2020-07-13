# maoyan_font_decryption
Comprehensive font decryption schema written in python
Recently, the font encryption technique is quite popularity used for Chinese sites, for prevent data scraping, the senstive data such as the numbers is encoded
using a special method - Font encryption, below is an example on maoyan.com (a popular movie site in Chinese)
![Maoyan.com - Font encryption](maoyan_font_screenshot.png)

Obviously, the numbers from HTML Source is encoded as HTML entities (unicode text), even you decode the HTML entities as unicode text, it's still messing unicode chars not the actual numbers as you desired.
```
<span class="index-left info-num one-line"><span class="stonefont">&#xea90;&#xe607;&#xe94e;&#xea90;&#xf351;</span></span>
```

# Solution
