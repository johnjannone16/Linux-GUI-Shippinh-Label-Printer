
# GUI for Generic Shipping Labels For Linux

A simple GUI that will automatically crop and rotate USPS shipping labels generated from eBay. I created this simply because the shipping label printer I bought has no GUI for Linux.  This is based off of the mobile app and Windows application that the printer was shipped with.

Double check that your printer profile is setup correctly double check that your label dimensions are what you set in the variables.

# Installation

This is packaged with a requirements.txt so create a .venv and run this command to grab all required packages:

```
pip install -r /path/to/requirements.txt
```
TODO: Generic installation video for drivers using cups

# Printer

For reference this is the printer I use and built this around:

https://www.amazon.com/gp/aw/d/B0C3V66NNK?psc=1&ref=ppx_pop_mob_b_asin_title

# Printer Installation
This is also based off of the above printer but I assume that the installation process will be the same for all of these generic thermal printers. My guess is that they all use the same base drivers for their thermal printers just  throw them in different cases.

**Driver location:**

https://support.pedoolo.com/support/solutions/articles/151000077768


For ubuntu based I then installed the drivers from the .deb file.

Open CUPS (2.4.1 at the time of writing) navigate to Printers>Modify Printers
If the Pedoolo drivers aren't set as default when nearing the end of modification browse for the drivers, they should be located under **/usr/share/cups/model/PEDOOLO** where you will find the .ppd

This should apply the default printer settings (i.e 100x150mm or 4x6in) and will allow you to send prints.

For now the printer needs to be connected via USB, unfortunately it looks like the printer auto disconnects if its not connecting via its official application.

You can run a test print using
```
lp -d printer_name /path/to/label.pdf
```
