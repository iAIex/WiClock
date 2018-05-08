# Widgets

This is a guide on how to write your own widgets for WiClock.  
**This guide is still a work in progress!**

## Tags
### What are they?
Each element displayed by your widget is represented by a tag. A tag looks like this: `[tagname_here]`. __
The name of the tag can be chosen freely within certain constraints/rules:__

To give a few examples:__

[MyText]__
type=text__
text=hallo__

[MyText]__
type=text__
text=world__

## [Variables]
Important: in the variables tag are nor calculation supported!__

| Attribute | Function |
| :-------- | :------- |
| a=1 | set variable a to 1 |
| b=2 | set variable b to 2 |
| c=hallo | set variable c to "hallo" |
| a=#b# | set a to b |
| a=$sec$ | set a to the second of the module values|
| str=#a# #c# | will result in "1 hallo" |

## [Calculations]
Here you can calculate with variables. Be careful, there is no string manipulation supported!__
Supported operations are: +, -, *, /, %, (, )__

| Attribute | Function |
| :-------- | :------- |
| a=1 | set a to 1|
| b=#a#+2 | set b to "1+2" result in 3 |
| c=(#b#+1)*2 | set c to "(1+2+1)*2" result in 8 |
## Attributes
Now you know what tags are but at the moment they don't really do anything. __
To now get things going each tag needs attributes. __
Some attributes are present in all tags and some are specific to certain types. General attributes are:__

| Attribute | Function |
| :-------- | :------- |
| type | defines the type of the tag (types are listed separately below) |
| x | defines the x position at which the tag should be rendered (top left corner) |
| y | defines the y position at which the tag should be rendered (top left corner) |
| height | height when rendering the tag. Overflow will be clipped |
| width | width when rendering the tag. Overflow will be clipped |

Since other sets of attributes are specific for certain types we grouped them by type here:__

### type=text
As the name suggests this type can dispaly text (and numbers)__

| Attribute | Value/Example | Function |
| :-------- | :-----: | :------- |
| text | Hello World | The text you want to display |
| font | defaultFont | The font used |
| startx | the x coordinate where the text starts |
| starty | the y coordinate where the text starts |

Example:__
[text]__
type=text__
text=123456__
font=default3x5__
colour=0,0,0__
startx=0__
starty=0__


### type=source__
This type of tag can display icons stored in resource files. A * at the beginning of the source name, will look for a__
source in the widget folder, otherwise resource file from /sources will be used.__

| Attribute | Value/Example | Function |
| :-------- | :-----: | :------- |
| source | star | the resource file that should be displayed |
| framerate | Integer | framerate for animated icons, defaults to 0 if this attribute is omitted (static icon) |
| startx | the x coordinate where the source starts |
| starty | the y coordinate where the source starts |

Example:__
[source]__
type=smiley__
startx=0__
starty=0__
colour=0,0,0__

### type=point__
Set a pixel at given position to colour.__

Example__
[point]__
type=point__
x=0__
y=0__
colour=1,1,1__

## IfConditions__
In evrey tag you can use as much IfConditions as you want, but you have to start with IfCondition, IfCondition1,__
IfCondition2 ... IfCondition99 and the numbers in a row.__
Every condition has one TrueAction and/or one FalseAction.__

| logic operations | function | example |
| :--------------- | :------- | :--------|
| == | is equal to | (1==1) result in True |
| != | is not equal to | (1!=1) result in False |
| > | greater than | (1>0) result in True |
| < | less than | (1<0) result in Fasle |
| >= | equal or greater than | (2>=0) result in False |
| <= | equal or less than | (2>=2) result in True |
| && | bitwise and | (1==1)&&(1>2) -> True && False result in False |
| || | bitwise or | (1==1)||(1>2) -> True || False result in True |

If condition is True TrueAction will be activated, otherwise FalseAction.__
At the True and False-Action you can manipulate attributes in the actual tag. NOT EVEN MORE!__

## Example of a basic watch:

[Calculations]__
a=$sec$%2__

[Watch]__
startx=2__
starty=1__
type=text
text=$hrs$:$mins$:$secs$__

IfCondition=(#a#==0)__
IfTrueAction=(text=$hrs$ $mins$ $secs$)__
IfFalseAction=(text=$hrs$:$mins$:$secs$)__
