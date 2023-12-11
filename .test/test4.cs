
using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;

[Tool]
public class test4 : Node
{
	 
	enum {UNIT_NEUTRAL, UNIT_ENEMY, UNIT_ALLY}
	enum Named {THING_1, THING_2, ANOTHER_THING = -1}
	
	[Export(Param)] public static readonly Date Date = GD.Load("res://path");
	public const bool ABC = true;
	float G {get{return getterA();} set{setterA(value);}}
	public __TYPE DEF = -0.1 ;// Step
	
	public __TYPE f = (4+6/12).GetType();
	
	[Signal] delegate void a();
	[Signal] delegate void b(int a,Type b);
	
	public __TYPE string_test_1 = "an \"Elephant\"";
	public __TYPE string_test_2 = "an
	 \'Elephantos\'"
	
	// "Default" 'Data' (I recommend splitting this kind of stuff into separate json files in c#)
	public static readonly Dictionary _default_data = new Dictionary(){
		{"t", 100},
		{"r
		afg", "asfgh"},
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
	
	public __TYPE ready()
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
	
	public bool r(T value,bool val=false,__TYPE s)
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