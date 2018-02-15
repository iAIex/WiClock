# Widgets

This is a guide on how to write your own widgets for WiClock.
This guide is still a work in progress!

## Tags
### What are they?
Each element displayed by your widget is represented by a tag. A tag looks like this: `[tagname_here]`. The name of the tag can be chosen freely within certain constraints/rules:
1. Tagnames must be unique within your widget  
   * If two tags share the same name the tag which comes last in your widget file "wins"
2. Some tagnames are reserved for special use  
   * E.g. the `[Meta]` tag (more on this later)
3. The `[Meta]` tag must be present somewhere in your widget  
   * It is advised to put this tag at the beginning of the file so it can easily be found by a human reader

To give a few examples:
```
[MyText]
type=text
content="hello"

[MyText]
type=text
content="world"
```
Since both tags are called "MyText" the tag with the `content="world"` would be the element that is displayed in the end, since it is further down in the widget.

### The Meta Tags
The Meta tag contains information on the widget (like size, name, etc). This tag is obligatory for every widget. As mentioned above we advise to put this tag at the very beginning of your widget file although it can be placed anywhere in your widget file.

## Attributes
Now you know what tags are but at the moment they don't really do anything. To now get things going each tag needs attributes. Some attributes are present in all tags and some are specific to certain types. General attributes are:

| Attribute | Function |
| :-------- | :------- |
| type | defines the type of the tag (types are listed separately below) |
| x | defines the x position at which the tag should be rendered (top left corner) |
| y | defines the y position at which the tag should be rendered (top left corner) |
| height | height when rendering the tag. Overflow will be clipped |
| width | width when rendering the tag. Overflow will be clipped |
