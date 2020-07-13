# maoyan_font_decryption
The numeric decryption solution for maoyan.com written in python, it could be used for general sites who uses same encryption technique.

Recently, the font encryption technique is quite popularity used for Chinese sites, for prevent data scraping, the senstive data such as the numbers is encoded
using a special method - Font encryption, below is an example on maoyan.com (a popular movie site in Chinese)
![Maoyan.com - Font encryption](maoyan_font_screenshot.png)

Obviously, the numbers from HTML Source is encoded as HTML entities (unicode text), even you decode the HTML entities as unicode text, it's still messing unicode chars not the actual numbers as you desired.
```
<span class="index-left info-num one-line"><span class="stonefont">&#xea90;&#xe607;&#xe94e;&#xea90;&#xf351;</span></span>
```

# Major module - [font_decrypt.py](font_decrypt.py)
It is the major module to decrypt the numbers encrypted in Font. 
In general, you might just exploit the below two methods to decrypt the numbers :
### decryptHtmlNumbers
**Parameter -'s'** is the original HTML entity text that looks like 
&amp;#xF09F;&amp;#xE690;&amp;#xEA64;&amp;#xF031;&amp;#xE238;&amp#xF031;
&amp;#xE238;.&amp#xF031;
**Note**, the 'dot' char is allowed.
**Parameter - 'font'** can be either url or local font file path, when 'http://' or 'https://' is leading of this parameter, it's treated as font url ,
otherwise, it's a local font file path.
**Returns** the actual numbers displaying on HTML page.

### decryptRawNumbers
It's same usage as decryptHtmlNumbers, except for the parameter - 's' should be raw unicode text

# Background principle
As mentioned before, the encrypted numbers can be seen in HTML source:
```
<span class="index-left info-num one-line"><span class="stonefont">&#xea90;&#xe607;&#xe94e;&#xea90;&#xf351;</span></span>
```
Figuring out that the displaying text is rely on font-family: stonefont
```
.stonefont {
    font-family: stonefont;
}
```
And the actual font file in here:
```
  <style>
    @font-face {
      font-family: stonefont;
      src: url('//vfile.meituan.net/colorstone/ceac9a4fb813b00f2c681b4dae3c4c773456.eot');
      src: url('//vfile.meituan.net/colorstone/ceac9a4fb813b00f2c681b4dae3c4c773456.eot?#iefix') format('embedded-opentype'),
           url('//vfile.meituan.net/colorstone/259b2a69d2fedfed719b8dcfe9c3a0022284.woff') format('woff');
    }

    .stonefont {
      font-family: stonefont;
    }
  </style>
```
Font file has defined the character mapping table which specific character code(in unicode) corresponds to certain glyph contours,
we can easily figure out the mapping table by the tool [Font Creator](https://www.high-logic.com/font-editor/fontcreator)

![Font creator - extracting the cmap table](font_creator.png)
