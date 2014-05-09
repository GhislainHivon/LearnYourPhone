# Learn your phone
A simple app to help children learn their phone number. The child must place the digits in a box with the same color (the box alpha is lower). When a digit is place in the correct box, it disappear and the digit is frozen in place. When all the digits are correctly place, a simple "Tada sound" (see LICENSE for details) can be heard and the digits "dance". The child can restart the game and play again.

## Installation and running
There is no special installations needed for "Learn your phone". Follow the instructions to install [Kivy](http://kivy.org/#download) for your os. Run "Learn your phone" as any other Kivy app on your os.

### My target
#### Android 4.3 (Samsung Galaxy S3)
I used the [Kivy launcher](http://kivy.org/docs/guide/packaging-android.html#packaging-your-application-for-kivy-launcher)

### How I tested "Learn your phone"
#### Windows 7
I used the [portable version](http://kivy.org/docs/installation/installation-windows.html#installing-the-portable-version)
#### Linux
##### Ubuntu 14.10
I used the [software package](http://kivy.org/docs/installation/installation-linux.html#ubuntu-kubuntu-xubuntu-lubuntu-oneiric-and-above)
##### Fedora 17
By [providing dependencies](http://kivy.org/docs/installation/installation-linux.html#providing-dependencies)

### First run
On the first run, you need to enter your phone number in the settings to be able to play the game.

### Subsequent runs
If the phone number is define in the settings, "Learn your phone" will start directly with the game ready to play.

## Features
### Digits only
You can enter any string of digits as your phone number. No minimum needed (but 1-3 digits look lonely) and no maximum (but 14+ make the answer box too little for comfort). That mean you can add digits as your child learn them or remove the regional code or even used "Learn your phone" for any sequence of digits you can think of.

### Hints
#### Color
I used soft, pastel color for the digits and their corresponding box. Also, the color are always assign in the same way, aka the first number is alway red, then going toward yellow, green, blue before returning towards red.
#### Font size
Small digits start on the left and big digits finish on the right

#### None of that matter
I think that a child should not be penalized if she remember the correct order for the digit and bypass the hint system: any valid digit is accepted in the box without consideration for color or size. This also help when, like me, your phone number got a repetition of a digit next to each other (not a big difference in size nor color).

## Limitations
### Apparent size vs Widget size
The active zone for a digit is bigger than the colored area. It's possible to have a digit a little outside of the box but it will still count as in the box for validation. I tried to balance the easiness of used with correct behavior.

### Overlaps of digits
Digits can be place and frozen one on top of the other. But I think that most of the time (under 12 digits), this is not a major hindrance to correctly guess which digit is the first.

## Future
This is a list of features that I will probably add after the contest end and if my daughter (the reason I build this) is still interested in this app.

+ A selection of phone numbers
+ Settings to remove hints (color, size)
+ Settings to deactivate regional code (the X first digits are not showed)
+ More hints
    + Vibrating the phone when the digit is in a good box
    + Flashing the answer in the box
+ More sounds
    + Voicing the phone number on victory
    + Or on demand as a hint