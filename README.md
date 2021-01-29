[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate?hosted_button_id=SP5PDHLKEMYFW)<br><br>
![](/icon_raw.svg)
# gd2cs.py
Regex based Python script that converts arbitrary gdscript code to C#<br>
Wrapped in a graphical UI plugin for use in the Godot Editor.<br>
It's far from perfect, but it it should let you skip most of the gruntwork when converting. <br> 
It analyzes syntax only. No fancy code analysis.
<br /> 
<br /> 
<b>Make sure to back-up all your files. No warranty of any kind is given. The author of this script cannot be held liable for any damage it may cause. <br><br>Use at your own risk.</b> <br><br>
Known issues :<br>
\- Keywords in strings or comments may be replaced<br>
\- Ternary operators such as A?B:C are too expensive to parse correctly and are therefore ignored in some transformations.<br>
<br>
Usage : <br>
In Godot:<br>
Just drop the addon directly into your godot projects addon folder, then activate it in your Project Settings.<br>
Then navigate to Project->Tools->gd2cs .<br>
Hover over buttons or input controls to find out what they do. <br>
<br>
From Python:<br>
Specify the input gd file via -f "\*" and the target output file via -o "\*" . <br>
Use -t * to specify the number of spaces in a tab (default = 4). This will replace consecutive spaces with tabs so the regex patterns can match a mix of space-offsets and tab-offsets (eg "else:\n&nbsp;&nbsp;&nbsp;&nbsp;pass" will become "else:\n\tpass").<br>
<br>
Example :<br>
python3 gd2cs.py/gd2cs.py -i "Test_Script_Godot.gd" -o "Output/TestScript.cs"<br>
<br>
Example Code Conversion (apr. real life example. Intentionally formatted badly to show where the converter will fail) :<br>
```GDScript
tool
extends Node


enum {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
enum Named {THING_1, THING_2, ANOTHER_THING = -1}

export(Date,Param)      const Date = preload("res://path")
const ABC = true
var G:float setget setterA, getterA
var DEF = -0.1 # Step

var f = typeof(4+6/12)

signal a()
signal b(a:int,b:Type)

var string_test_1 = 'an "Elephant"'
var string_test_2 = 'an
 \'Elephantos\''

# "Default" 'Data' (I recommend splitting this kind of stuff into separate json files in c#)
const _default_data = {
	"t" : 100,
	"r
	afg" : 'asfgh',
	"u" : false,# Example Comment
	"r":["a",{"b":false}],
	"t":{"e":{"g":1,"f":2},},
};

func setterA(v:float):
	return
	pass

func getterA()->float:
	return 1.

func ready():
	var s = range(abs(-1),randi())
	
	.ready();

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
			
func default_async_function():
	yield(self,'a');
			
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
	 
	enum {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY};
	enum Named {THING_1, THING_2, ANOTHER_THING = -1}
	
	[Export(Param)] static readonly Date Date = GD.Load("res://path");
	const bool ABC = true;
	float G {get{return getterA();} set{setterA(value);}}
	float DEF = -0.1f ;// Step
	
	__TYPE__ f = (4+6/12).GetType();
	
	[Signal] delegate void a();
	[Signal] delegate void b(int a,Type b);
	
	string string_test_1 = "an \"Elephant\"";
	__TYPE__ string_test_2 = "an\n"+
	" \'Elephantos\'"
	
	// "Default" 'Data' (I recommend splitting this kind of stuff into separate json files in c#)
	static readonly Dictionary _default_data = new Dictionary(){
		{"t", 100},
		{"r\n"+
	"	afg", "asfgh"},
		{"u", false},// Example Comment
		{"r",new Array(){"a",new Dictionary(){{"b",false}}}},
		{"t",new Dictionary(){{"e",new Dictionary(){{"g",1},{"f",2}}},}},
	};
	
	public void setterA(float v)
	{  
		return;
	
	}
	
	public float getterA()
	{  
		return 1.;
	
	}
	
	public __TYPE__ ready()
	{  
		var s = GD.Range(Mathf.Abs(-1),GD.Randi());
		
		base.ready();
	
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
	
	public bool r(T value,bool val=false,__TYPE__ s)
	{  
		if(value == null)
			 return !true;
	
		var type = (value).GetType();
		switch( type )
		{
			case typeof(bool):
			case typeof(int):
			case null:
				return value;
				break;
			case typeof(Dictionary):
				Dictionary result = new Dictionary(){};
				foreach(var k in value)
				{
					result[k] = value[k];
				}
				return result;
				
				break;
		}
	}
	
	public async void default_async_function()
	{  
		await ToSignal(this,"a");
	}
	
				
}
```

As you can see, it's not perfect and it will require you to manually fix the formatting and some underivable type definitions afterwards. But it should save you hundreds of hours on your code conversions. If it does save you time, please consider leaving a donation. It'll flow right back into making this project even better.

<br>

What's next :<br>

Smarter Analysis :<br> 

\- Project-wide class analysis : Scan existing gd and cs scripts, extract classes, methods, fields, and use data to more accurately rename, to automatically load scripts, to infer function return types, etc <br>

\- Optional automatic PascalCase conversion on all non-static variables<br>

\- process entire folders (recursively)<br>
<br>

But before that the focus will be on polishing existing features, increasing performance and publishing it on the Godot Asset Store.<br>
