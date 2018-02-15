# Widgets

This is a guide on how to write your own widgets for WiClock.
This guide is still a work in progress!

## Tags
Each element displayed by your widget is represented by a tag. A tag looks like this: `[tagname_here]`. The name of the tag can be chosen freely within certain constraints/rules:
1. Tagnames must be unique within your widget  
   * If two tags share the same name the tag which comes last in your widget file "wins"
2. Some tagnames are reserved for special use  
   * E.g. the `[Meta]` (more on this later)
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
Since both tags are called "MyText" the tag with the content="world" would be the element that is displayed in the end, since it is further down in the widget.
