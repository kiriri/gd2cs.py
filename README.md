[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate?hosted_button_id=SP5PDHLKEMYFW)

# gd2cs.py
Regex based Python script that converts arbitrary gdscript code to C#<br>
It's far from perfect, but it it should let you skip most of the gruntwork when converting. <br> 
It analyzes syntax only. No fancy code analysis.
<br /> 
<br /> 
<b>Make sure to back-up all your files. No warranty of any kind is given. The author of this script cannot be held liable for any damage it may cause. <br><br>Use at your own risk.</b> <br><br>
Known issues :<br>
\- Keywords in strings or comments may be replaced<br>
\- Nested Dictionaries generate excessive/invalid semicolons<br>
<br>
Usage : <br>specify the input gd file via -f "\*" and the target output file via -o "\*" . <br>
<br>
Example :<br>
python3 gd2cs.py/gd2cs.py -i "Test_Script_Godot.gd" -o "Output/TestScript.cs"<br>
<br>
Example Code Conversion (apr. real life example. Intentionally formatted badly to show where the converter will fail) :<br>
```python
tool
extends Node

export(Date,Param)      const Date = preload("path")
const ABC = true
var DEF = 0.1 # Step

var f = typeof(4+6/12)

signal a()
signal b(a:int,b:Type)


# Default Data (I recommend splitting this kind of stuff into separate json files in c#)
const _default_data = {
	"t" : 100,
	"r" : 'asfgh',
	"u" : false,# Example Comment
	"r":["a",{"b":false}],
	"t":{"e":{"g":1,"f":2},},
};


func ready():
	var s = range(abs(-1),randi())
	
    if ABC: # Comment
        assert(false)
    elif false:
        print("Hello"+" "+"World")
    else:
        (a+b)()
    return [
    [0,e,[0,{}]], # a
    [1,{},[0,{}]],
    ];

# Do stuff
func r(value:T,val=false,s)->bool:
	if value == null : return !true
	
	var type = typeof(value)
	match type :
		TYPE_BOOL,TYPE_INT,TYPE_NIL:
			return value
		TYPE_DICTIONARY:
			var result = {}
			for k in value:
				result[k] = value[k]
			return result
			
			
```

<br>
<br>


Result :<br>

```cs

using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;

[Tool]
public class GameDataTest2 : Node
{
	 
	[Export(Param)] static readonly Date Date = GD.Load("path");
	const bool ABC = true;
	float DEF = 0.1f ;// Step
	
	var f = (4+6/12).GetType();
	
	[Signal] delegate void a();
	[Signal] delegate void b(int a,Type b);
	
	
	// Default Data (I recommend splitting this kind of stuff into separate json files in c//)
	static readonly Dictionary _default_data = new Dictionary(){
		{"t", 100},
		{"r", "asfgh"},
		{"u", false},// Example Comment
		{"r",new Array(){"a",new Dictionary(){{"b",false}}}},
		{"t",new Dictionary(){{"e",new Dictionary(){{"g",1},{"f",2}}},}},
	};
	
	
	public  ready()
	{  
		var s = GD.Range(Mathf.Abs(-1),GD.Randi());
		
	    if(ABC) // Comment
	    {
	        System.Diagnostics.Debug.Assert(false);
	    }
	    else if(false)
	    {
	        GD.Print("Hello"+" "+"World");
	    }
	    else
	    {
	        (a+b)()
	    }
	    return new Array(){
	    new Array(){0,e,new Array(){0,new Dictionary(){}}}, // a
	    new Array(){1,new Dictionary(){},new Array(){0,new Dictionary(){}}},
	    };
	
	// Do stuff
	}
	
	public bool r(T value,bool val=false,s)
	{  
		if(value == null)
			 return !true;
		
		var type = (value).GetType();
		switch( type )
		{
			case TYPE_BOOL:
			case TYPE_INT:
			case TYPE_NIL:
				return value;
				break;
			case TYPE_DICTIONARY:
				Dictionary result = new Dictionary(){};
				foreach(var k in value)
				{
					result[k] = value[k];
				}
				return result;
				
				break;
		}
	}
	
				
}
```

As you can see, it's not perfect and it will require you to manually fix the formatting and some underivable type definitions afterwards. But it should save you hundreds of hours on your code conversions. If it does save you time, please consider leaving a donation. It'll flow right back into making this project even better.

<br>
TODO:<br>
- ignore Comments and Strings<br>
- async functions (yield)<br>
- process entire folders (recursively)<br>
