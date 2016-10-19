
vars  = """\
recorder
recorder power supply
peak meter reading
gain control position
tape
tape speed
track
record local time
reference signal
temperature initial
temperature final
relative humidity initial
relative humidity final
light
extraneous noise
substrate
air movement
biotic factors
microphone
microphone distance from subject
microphone windshield
microphone reflector
microphone preamplifier
microphone filter"""


snippet = """
{{#if:{{{%(var)s|{{{%(var_capitalise)s|}}} }}}{{{demo|<noinclude>1</noinclude>}}}|
<tr valign="top">
<td class="fileinfo-paramfield">%(var_capitalise)s</td>
<td>{{{%(var)s|{{{%(var_capitalise)s|}}} }}}</td>
</tr>
}}
"""


if __name__ == "__main__":
    for var in vars.split('\n'):
        print(snippet % {
            'var_capitalise': var.capitalize(),
            'var': var})
