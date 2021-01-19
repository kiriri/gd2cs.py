""" gd2cs.py
Turn gdscript to c# via regex.
Make sure to back-up all your files. No warranty or of any kind is given. The author of this script cannot be held liable for any damage it may cause. Use at your own risk. 
Usage : specify the input gd file via -f "*" and the target output file via -o "*" . 
"""
__author__ = "Sven Hollesen"
__copyright__ = "Copyright 2021, Sven Hollesen"
__license__ = "GNU General Public License v3.0"
__version__ = "1.0.0"

import click
import os
import math
import sys


# regex module required, install if not already.
try:
  import regex
except ImportError:
	if click.confirm('This Script requires the regex package. Install?', default=True):
		if (sys.version_info > (3, 0)):
			os.system('python3 -m pip install regex')
		else:
			os.system('python -m pip install regex')
	else:
		quit()
try:
	import regex
except ImportError:
	print('Failed to install regex package. Try to do so manually. The command should look somewhat like\npython3 -m pip install regex\n')

## KNOWN ISSUES
# Keywords in strings or comments may be replaced
# Nested Dictionaries generate excessive/invalid semicolons


# TODO : yield => await ToSignal(sender, "signal");
# TODO : Mark functions async if they contain yield (not in comments!)
# TODO : Mark functions as void if they don't contain a return (with a valid_term)
# TODO : If extend Node, convert all Node function to capitalized forms
# TODO : Fix Comments in strings (don't convert!) (Use ?: to drop them?)
# TODO : Process entire folders at once, recursively -r flag

# Name of the file to be converted :
filename = "GameData.gd"#"gd2cs_test"#
outname = "GameDataTest.cs"

i = 0
while i < len(sys.argv):
	arg = sys.argv[i]
	if arg == "-f":
		filename = sys.argv[i+1]
		i+=2
	elif arg == "-o":
		outname = sys.argv[i+1]
		i+=2 
	else:
		i+=1

if not filename.endswith(".gd"):
	filename = filename + ".gd"


if not outname.endswith(".cs"):
	outname = filename + ".cs"




match_irrelevant = "((^\s*\n)|(\/\/.*\n))" # Irrelevant c#

any_char = "[\w\W]"
separator = fr"([{{}}\[\]\s,:;=()])"
comment_or_empty = "((^\s*\n)|(^\s*\/\/.*\n))"
reserved_keywords = fr"(public|static|var|const|foreach|for|if|else|switch|case|return|using)"
valid_name = fr"([_a-zA-Z]+[_\-a-zA-Z0-9]*(?<!{reserved_keywords}))" 
match_curlies = fr"(?<curlies>{{((?>[^{{}}]+)|(?&curlies))*}})" # Named group recursion on curled braces
match_braces = fr"(?<braces>\(((?>[^()]+)|(?&braces))*\))"
match_brackets = fr"(?<brackets>\[((?>[^\[\]]+)|(?&brackets))*\])"
builtin_constructors = fr"(String|Vector2|Rect2|Vector3|Color|Transform2D|Plane|Quat|AABB|Basis|Transform|NodePath|RID|Object|Array|Dictionary)"# gd builtins types. Ignore types that don't have matching constructor in c#, like float
builtin_type = fr"(bool|uint|int|float|double|string|object|sbyte|byte|long|ulong|short|ushort|decimal|char|DateTime)" # C# builtins
valid_bool = fr"(true|false|True|False)"
valid_int = fr"(-{{0,1}}[0-9]+)"
valid_string = fr"(\".*?(?<!\\)\")"
valid_float = fr"(-{{0,1}}([0-9]*\.[0-9]+|[0-9]+\.[0-9]*)f{{0,1}})"
valid_array = fr"({match_brackets})" # GD Definition
valid_dictionary = fr"{match_curlies}" # GD Definition
valid_value = fr"({valid_bool}|{valid_string}|{valid_float}|{valid_int}|{valid_array}|{valid_dictionary})"
valid_value_c = fr"({valid_bool}|{valid_string}|{valid_float}|{valid_int})"
op = fr"([\/%+\-*><]|\|\||&&|>=|<=|==|!=|\||&|\sin\s|\sas\s|\sis\s|\sand\s|\sor\s)" # Basic (binary) operators
op_l = fr"(new\s|!|not\s)" # Right binding operators
op_r = fr"({match_brackets}|{match_braces}|{match_curlies})" # Left binding operators
#fcall = fr"(?<!public .*)({valid_name}\s*{match_braces}\s*{match_curlies}*)" # Deprecated, function call is now an op_r
full_name = fr"({valid_name}((\.{valid_name})*))" # Full name, including all dot accessors
aterm = fr"({valid_value}|{valid_name})" # Atomic Terms without accessors (.)
aterm_c = fr"({valid_value_c}|{valid_name})" # Atomic Terms without accessors (.)
sterm = fr"(?<sterm>({aterm}|\((?&sterm)\))(\.{valid_name})*)" # Simple Terms without operators other than dot accessor
#cterm = fr"{aterm}({op_r}(\.{full_name}){0,1})*"
cterm = fr"(?<cterm>({aterm}|\((?&cterm)\))(\s*?{op_r}|\.{valid_name})*)" # Closed Terms without operators other than accessors of any kind
cterm_c = fr"(?<cterm>({aterm_c}|\((?&cterm)\))(\s*?{op_r}|\.{valid_name})*)" # Closed Terms without operators other than accessors of any kind
#valid_term = fr"(({op_l}\s*)*{sterm}(\s*{op_r})*((\s*{op}\s*({op_l}\s*)*{sterm})(\s*{op_r})*|\.[ \t]*{fcall}\s*{op_r}*)*)";
valid_term = fr"(?<termo>(?!\s)(({op_l})*\s*?({cterm}|\(\s*(?&termo)\s*?\))\s*?(\s*{op}\s*(?&termo))*))";
valid_term_c = fr"(?<termo>(?!\s)(({op_l})*\s*?({cterm_c}|\(\s*(?&termo)\s*?\))\s*?(\s*{op}\s*(?&termo))*))";
# valid_term = fr"(?!\s)(?<termo>({op_l})*\s*?({cterm}|\(\s*(?&termo)\s*?\))\s*?(\s*{op}\s*(?&termo))*)(?={separator})";
match_comments_old = fr"[ \t]*#.*$"
match_comments_new = fr"[ \t]*\/\/.*$"
match_eol = fr"(?<eol>({match_comments_old}|{match_comments_new}|[\t ])*?$)" # Remaining bits of the line, such as tabs, spaces, comments etc




# Default imports and aliases that almost every class needs.
header = """
using System;
using Godot;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;
""";

replacements = [
	# Clean up directives that are manually applied after regex replacements
	[fr"^(\s*)tool\s*$"," "], 
	[fr"^(\s*)extends\s*.*\s*$"," "],
	# Turn lowest level unprocessed dictionaries. KV pairs are still of form K:V though
	[fr"(?<!(new Dictionary\(\)|[\w\W]{{5}}new Array\(\)))(?<=([:,={{[(]|return\s+))(?P<W>{match_eol}*\s*)(?P<C>{match_curlies})",r"\g<W>new Dictionary()\g<C>"], 
	# Same for array
	[fr"(?<!(new Dictionary\(\)|new Array\(\)))(?<=(([:,={{[(]|return\s*)(\s*)))\[(([^\[]|(?R))*?)\]",r"new Array(){\5}"], 
	# Chars don't exist in gdscript, so let's assume all of those '-strings are normal "-strings.
	["\'","\""], 
	# Single line comments start with # ( TODO This may mess up strings though!)
	["#","//"], 
	# Variant is System.Object in C#
	[fr"(?<={separator})Variant(?={separator})",fr"System.Object"],
	# For loops
	[fr"(?<=\n)([\t ]*)for[ ]+(.*)(->(.*))*:(.*)\n(((\1[\t ]+.*\n)|{comment_or_empty})*)",r"\1foreach(var \2)\5\n\1{\n\6\1}\n"], 
	# Variable definitions, if they have a valid type
	[fr"var[\t ]+(?P<Name>{valid_name})[\t ]*:[\t ]*(?P<Type>{valid_name})(?= *[=\n])",r"\g<Type> \g<Name>"], 

	## Functions

	# Function arguments, if they have a valid type
	[fr"(?<!\/\/.*)(?<={valid_name}[\t ]*\( *.*)(?P<Name>{valid_name})[\t ]*:[\t ]*(?P<Type>{valid_name})",r"\g<Type> \g<Name>"], 
	# replace function declarations, if possible use return type, otherwise leave blank
	[fr"(?P<A>[\t ]*)func[\t ]+(?P<Name>{valid_name})[\t ]*(?P<Params>{match_braces})([\t ]*->[\t ]*(?P<R_Type>.*))*[ \t]*:(?P<Comments>.*)\n(?P<Content>((\1[\t ]+.*\n)|{comment_or_empty})*)",r"\1public \g<R_Type> \g<Name>\g<Params>\n\1{\1  \g<Comments>\n\g<Content>\1}\n\n"], 
	# autocomplete function arguments via default values (bool). First limit selection to function signature, then run replacement over that section only.
	[[fr"(?<=^\s*public[\t ]+({valid_name}[\t ]+){{0,1}}{valid_name}[\t ]*){match_braces}",
	fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*{valid_bool})"],fr"bool \g<A>"],
	# autocomplete function arguments via default values (int)
	[[fr"(?<=^\s*public[\t ]+({valid_name}[\t ]+){{0,1}}{valid_name}[\t ]*){match_braces}",
	fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*{valid_int})"],fr"int \g<A>"],
	# autocomplete function arguments via default values (string)
	[[fr"(?<=^\s*public[\t ]+({valid_name}[\t ]+){{0,1}}{valid_name}[\t ]*){match_braces}",
	fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*{valid_string})"],fr"string \g<A>"],
	# autocomplete function arguments via default values (float)
	[[fr"(?<=^\s*public[\t ]+({valid_name}[\t ]+){{0,1}}{valid_name}[\t ]*){match_braces}",
	fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*{valid_float})"],fr"float \g<A>"],
	# autocomplete function arguments via default values (new T)
	[[fr"(?<=^\s*public[\t ]+({valid_name}[\t ]+){{0,1}}{valid_name}[\t ]*){match_braces}",
	fr"(?<=[,(]\s*?)(?P<A>{valid_name}\s*=\s*new\s+(?P<Name>{full_name}))"],fr"\g<Name> \g<A>"],

	## If/Else

	# replace if/elif blocks 
	[fr"^(?P<A>[ \t]*)(?P<B>if|elif)(?=[\t \(])[\t ]*(?P<C>({valid_term}){{1,1}})[ \t]*:(?P<D>[^\n]*?)(?P<Comment>{match_eol})(?P<E>\n({comment_or_empty}*(\1[\t ]+.*\n)*))",r"\g<A>\g<B>(\g<C>)\g<Comment>\n\g<A>{\g<D>\n\g<E>\n\g<A>}\n"], 
	# elif
	[fr"(?<={separator})elif(?={separator})","else if"],
	 # replace else
	[fr"^(?P<A>[ \t]*)(?P<B>else)[\t ]*:(?P<D>[^\n]*)\n(?P<E>((\1[\t ]+.*(\n|$)|{comment_or_empty})*))",r"\g<A>\g<B>\g<D>\n\g<A>{\n\g<E>\n\g<A>}\n"],
	# Inline if else
	[fr"((?=[^\n]*[\t ]+if[ \t]+[^\n]+[ \t]+else[ \t]+[^\n]+)(?P<A>{valid_term})[ \t]+if[ \t]+(?P<B>{valid_term})[ \t]+else[ \t]+(?P<C>{valid_term}))",fr"\g<B> ? \g<A> : \g<C>"],

	## Variable Declarations

	# Signals
	[fr"(?<={separator})signal(?P<R>\s+{valid_name}\s*{match_braces})[\t ]*\;*(?={match_eol})",fr"[Signal] delegate void\g<R>;"],
	# Unidentifiable variables const var
	[fr"(?<={separator}const\s+)(?={valid_name}\s*=)",r"var "], 
	# Auto identify variables from export hints
	[fr"(?<={separator})export\s*\(\s*(?P<T>{valid_term})\s*(,\s*(?P<A>.*?){{0,1}})\s*\)\s*(?P<B>(const\s+){{0,1}})var(?=\s+{valid_name}\s*=)",fr"[Export(\g<A>)] \g<B> \g<T>"],
	# Auto identify bools. TODO : Also accept simple static terms such as 5*5, !true, "a" in ["a","b","c"]
	[fr"(?<={separator})var(?=\s+{valid_name}\s*=\s*{valid_bool}(.*))",r"bool"],
	# Auto identify float
	[fr"(?<={separator})var(?P<A>\s+{valid_name}\s*=\s*{valid_float})",r"float\g<A>f"],  
	# Auto identify integers. 
	[fr"(?<={separator})var(?=\s+{valid_name}\s*=\s*{valid_int}(.*))",r"int"], 
	# Auto identify string
	[fr"(?<={separator})var(?=\s+{valid_name}\s*=\s*{valid_string}(.*))",r"string"], 
	# Auto identify Object
	[fr"(?<=\s|^)var\s+(?P<A>{valid_name})(?=\s*=\s*new\s+(?P<B>{full_name})(.*))",fr"\g<B> \g<A>"], 
	# const => static readonly unless value is struct
	[fr"const[\t ]+(?!{builtin_type}[\t ])(?={valid_name}[\t ]+{valid_name}[\t ]+=)",fr"static readonly "],
	
	## Operators

	# not => !
	[fr"(?<={separator})not(?=[\s(])\s*","!"], 
	# Direct casts
	[fr"(?<={separator})(\s*){builtin_type}\s*\(",fr"\2(\3)("], 
	 # Builtin constructors, like "Vector2()" => "new Vector2()"
	[fr"(?<={separator})(?<!new\s+)(?P<A>\s*)(?P<B>{builtin_constructors})\s*\(",fr"\g<A>new \g<B>("],
	# typeof(v) => v.GetType()
	[fr"(?<={separator}\s*)typeof\s*{match_braces}",r"\2.GetType()"], 
	# TODO : Don't affect strings and comments
	[r"(?<=\s)and(?=\s)","&&"], 
	[r"(?<=\s)or(?=\s)","||"],
	# [fr"{cterm}\s+in\s+{cterm}",fr""] # Ignore "in" operator for now due to complicated operator binding situation.
	# Turn all remaining A : B into automatic array pairs {A,B} , presumably part of dictionary initiation.
	[fr"(?<! \/\/.*)(\"(([^\"]|\\\")*?)((?<!\\)\"))(\s*)(:)(((?<curlies>{{((?>[^{{}}]+)|(?&curlies))*}})|([^{{]))*?)(?=}}|,)",r"{\1,\7}"],

	## SWITCH/CASE

	# Multistep. Match iteratively on previous match only. Last match is used with replacement regex. Then all pieces are merged back together again. This is me surrendering to the almighty switch/case pattern, which I just can't manage to squeeze into a single regex replacement line. I know possessive quantifiers should be able to help here, but the effort is just not worth it since I don't have a testing tool that supports those
	[[fr"^([ \t]*)match[ \t]+(.*)[ \t]*:.*\n({comment_or_empty}|\1[ \t]+.*\n)*",fr"^([ \t]*)(?!case)(({valid_term}(\s*,\s*{valid_term})*)[ \t]*:(.*)\n({comment_or_empty}|\1[ \t]+.*\n)*)"],fr"\1case \2\1\tbreak;\n"], 
	 # Continue switch case : turn match to switch and surround with curlies.
	[fr"^(?P<A>[ \t]*)match(?P<B>[ \t]+{valid_term}[ \t]*):(?P<C>[ \t]*(\/\/.*)*\n)(?P<D>({comment_or_empty}|\1[ \t]+.*\n)*)",fr"\g<A>switch(\g<B>)\g<C>\g<A>{{\n\g<D>\g<A>}}\n"],
	# C# Doesn't support multiple cases in one line, so split them
	[fr"^(?P<A>\s+)case\s+(?P<B>{valid_term})\s*,\s*(?P<C>({valid_term},)*{valid_term})\s*:",fr"\g<A>case \g<B>:\n\g<A>case \g<C>:"], 

	## SEMICOLONS

	# semicolon at end of standalone terms (such as function calls)
	[fr"(?<![,]\s*)(?<=^[ \t]*)(?!{reserved_keywords}\s*\(*)(?P<Content>{valid_term_c}[ \t]*)(?P<Comment>{match_eol})(?!\s*[{{[(])",fr"\g<Content>;\g<Comment>"], 
	# semicolon at end of assignments
	[fr"((?<=^[ \t]*|((var|const|public|private|static|async|delegate|{match_brackets})[ \t])*)({valid_name} ){{0,1}}{valid_term}[\t ]*[\+\-]{{0,1}}=[\t ]*{valid_term}[ \t]*)(?P<E>{match_eol})(?!\s*[{{(])",fr"\1;\g<E>"], 
	# return statements TODO : May be surrounded by braces or curlies, which will not count as ^ or $ 
	[fr"^(?P<A>[ \t]*return([\t ]*{valid_term}){{0,1}})(?P<B>{match_eol})",fr"\g<A>;\g<B>"], 

	[fr"^[\t ]*pass[\t ]*;*[\t ]*\n",""], # Strip "pass", which is replaced already by (maybe empty) curlies.

];


function_replacements = [
	["Color8","Color.Color8"],
	["type_exists","GD.TypeExists"],
	["var2str","GD.Var2Str"],
	["str2var","GD.Str2Var"],
	["str","GD.Str"],
	["range","GD.Range"],
	["rand_seed","GD.RandSeed"],
	["rand_range","GD.RandRange"],
	["randomize","GD.Randomize"],
	["randi","GD.Randi"],
	["randf","GD.Randf"],
	["seed","GD.Seed"],
	["var2bytes","GD.Var2Bytes"],
	["bytes2var","GD.Bytes2Var"],
	["print","GD.Print"],
	["print_stack","GD.PrintStack"],
	["prints","GD.PrintS"],
	["printraw","GD.PrintRaw"],
	["printerr","GD.PrintErr"],
	["push_error","GD.PushError"],
	["push_warning","GD.PushWarning"],
	["load","GD.Load"],
	["linear2db","GD.Linear2Db"],
	["db2linear","GD.Db2Linear"],
	["hash","GD.Hash"],
	["instance_from_id","GD.InstanceFromId"],
	["funcref","GD.FuncRef"],
	["dectime","GD.DecTime"],
	["convert","GD.Convert"],
	["assert","System.Diagnostics.Debug.Assert"],
	["max","Mathf.Max"],
	["min","Mathf.Min"],
	["abs","Mathf.Abs"],
	["acos","Mathf.Acos"],
	["asin","Mathf.Asin"],
	["atan","Mathf.Atan"],
	["atan2","Mathf.Atan2"],
	["cartesian2polar","Mathf.Cartesian2Polar"],
	["ceil","Mathf.Ceil"],
	["char","Char.ConvertFromUtf32"],
	["clamp","Mathf.Clamp"],
	["cos","Mathf.Cos"],
	["cosh","Mathf.Cosh"],
	["decimals","Mathf.StepDecimals"],
	["deg2rad","Mathf.Deg2Rad"],
	#["dict2inst","Mathf.Abs"],
	["ease","Mathf.Ease"],
	["exp","Mathf.Exp"],
	["floor","Mathf.Floor"],
	["fmod","Mathf.PosMod"],
	["fposmod","Mathf.PosMod"],
	#["get_stack","Mathf.Abs"],
	#["inst2dict","Mathf.Abs"],
	["inverse_lerp","Mathf.InverseLerp"],
	["is_equal_approx","Mathf.IsEqualApprox"],
	["is_inf","Mathf.IsInf"],
	#["is_instance_valid","Mathf.Abs"],
	["is_nan","Mathf.IsNaN"],
	["is_zero_approx","Mathf.IsZeroApprox"],
	#["len","Mathf.Abs"],
	["lerp","Mathf.Lerp"],
	["lerp_angle","Mathf.LerpAngle"],
	["log","Mathf.Log"],
	["move_toward","Mathf.MoveToward"],
	["nearest_po2","Mathf.NearestPo2"],
	["ord","Char.ConvertToUtf32"],
	["parse_json","Godot.JSON.Parse"],
	["polar2cartesian","Mathf.Polar2Cartesian"],
	["posmod","Mathf.PosMod"],
	["pow","Mathf.Pow"],
	["preload","GD.Load"],
	#["print_debug","Mathf.Abs"],
	["rad2deg","Mathf.Rad2Deg"],
	["range_lerp","Mathf.Lerp"],
	["round","Mathf.Round"],
	["seed","GD.Seed"],
	["sign","Mathf.Sign"],
	["sin","Mathf.Sin"],
	["sinh","Mathf.Sinh"],
	["smoothstep","Mathf.Smoothstep"],
	["sqrt","Mathf.Sqrt"],
	["step_decimals","Mathf.StepDecimals"],
	["stepify","Mathf.Stepify"],
	["tan","Mathf.Tan"],
	["tanh","Mathf.Tanh"],
	["to_json","Godot.JSON.Print"],
	#["validate_json","Mathf.Abs"],
	#["weakref","Mathf.Abs"],
	["wrapf","Mathf.Wrap"],
	["wrapi","Mathf.Wrap"],
	#["yield","Mathf.Abs"],
	["emit_signal","EmitSignal"],
	["connect","Connect"],
]



# Regex doesn't support recursion of groups that share a name with previously defined groups.
# The next 2 functions append a number to each group to make them unique to the compiler.
# (This should not affect the actual logic and can be safely ignored)
unique_number = 0
def make_group_unique(reg_data):
	global unique_number
	unique_number += 1

	precise_match = regex.match(fr"(\(\?\<([a-zA-Z]+)\>)(.*)\)",reg_data[0],flags);

	content = strip_duplicate_groups(precise_match[3])

	return (precise_match[1] + content + ')').replace(precise_match[2],precise_match[2]+str(unique_number))

# Recursion doesn't work with duplicate group names, so rename them if they don't already have a number suffix (suffix => presumed renamed)
def strip_duplicate_groups(reg):
	prev = reg
	result = regex.subf(fr"(?=\(\?\<([a-zA-Z])+\>)({match_braces})",make_group_unique,prev)
	return result


# Regex search flags. Multiline allows the use of ^ for the beginning of a line and $ for the end.
flags = regex.MULTILINE or regex.GLOBAL_FLAGS


# Replace in multiple steps, by matching first
def replace_matches(matches,replacement,text,depth=0):
	sub_segment = matches[depth];
	

	matches[depth] = strip_duplicate_groups(matches[depth])
	
	if len(matches)-1 == depth:
		loop_count = 0
		while True:
			loop_count+=1
			if loop_count > 100:
				print('Infinite loop detected')
				print(text)
				quit()
			prev_text = text
			text = regex.sub(matches[depth], replacement, text,0,flags)
			if text == prev_text: # Repeatedly apply same operation until no more changes occur.
				return text;
	else:
		result =  regex.subf(matches[depth],lambda v : replace_matches(matches,replacement,v.group(0),depth+1) ,text,0,flags)
		return result;
	

# Open the file in read/write mode
with open(filename,'r+') as f:
	text = f.read()
	
	print("PROCESSING -- " + filename)

	orig_text = text;

	extending = regex.findall(r"extends (.*)\n",text);
	if extending :
		extending = extending[0]
	else:
		extending = "Godot.Object"
	tool = len(regex.findall(r"^tool.*$",text,flags)) > 0

	for pair in replacements:
		
		while True:
			prev_text = text
			if isinstance(pair[0], str): # is string
				pair[0] = strip_duplicate_groups(pair[0])
				text = regex.sub(pair[0], pair[1], text,0,flags)
			else: # Is array
				text = replace_matches(pair[0],pair[1],text)
			if text == prev_text: # Repeatedly apply same operation until no more changes occur.
					break;
			if len(text) > len(orig_text) * 2:
				print("SIZE DOUBLED, PRESUMED INFINITE BLOAT.")
				break;


	for pair in function_replacements:
		pair[0] = fr"(?<={separator})" + pair[0] + fr"(?=\()";
		text = regex.sub(pair[0], pair[1], text,0,flags)
	
	text = regex.sub("^","\t",text,0,flags);

	class_name = regex.match(r'.*(?=\.cs)',outname)[0];
	text = f"{header}\n{'[Tool]' if tool else ''}\npublic class {class_name} : {extending}\n{{\n" + text + "\n}";
	with open(outname,'w') as wf:
		wf.write(text);
		print("SUCCESS -- " + outname)

# 	test_text = """
# export(Date,Param)const Date = preload("res://Scripts/Resources/Date.cs");
# export(Date,Param) const DEVMODE = true
# export ( Date , Param ) const TIMESTEP = 0.1 # Smallest undo step (determines (inversely) how smooth timetravel looks, but also how fast savegame size grows)


# 		"""

# 	print('==========================RESULT=============================')
# 	pattern = strip_duplicate_groups(fr"((?<={separator})export\s*\(\s*(?P<T>)\s*,\s*(?P<A>.*)\s*\)\s*(?P<B>(const\s+){{0,1}}var)(?=\s+{valid_name}\s*=))"); # TODO : Why not match this particular example?
# 	print("\n".join(list(map(lambda v : "["+v[0].replace("\n","\\n")+"]",regex.findall(pattern,test_text,flags)))))

	
