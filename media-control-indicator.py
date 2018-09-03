#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Playerctl', '1.0')
from gi.repository import Gtk
from gi.repository import AppIndicator3, Gio, GLib, GObject, Playerctl
from gi.repository.GdkPixbuf import Pixbuf 
from urllib.request import urlopen
import threading


class media_control_indicator:
    def __init__ (self):
        self.indicator = AppIndicator3.Indicator.new("media_control_indicator", "/usr/share/icons/Adwaita/32x32/actions/media-playback-stop.png", AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        self.menu = Gtk.Menu()
        self.indicator.set_menu(self.menu)
        
        self.albumartItem = Gtk.MenuItem()
        self.npItem = Gtk.MenuItem("Media control indicator")
        self.playButton = Gtk.ImageMenuItem("Play",image=Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
        self.previousButton = Gtk.ImageMenuItem("Previous",image=Gtk.Image(stock=Gtk.STOCK_MEDIA_PREVIOUS))
        self.nextButton = Gtk.ImageMenuItem("Next",image=Gtk.Image(stock=Gtk.STOCK_MEDIA_NEXT))
        
        self.playButton.connect('activate',self.mediaPlay)
        self.previousButton.connect('activate',self.mediaPrevious)
        self.nextButton.connect('activate',self.mediaNext)
        
        self.albumArt = Gtk.Image()
        self.albumartItem.add(self.albumArt)
        
        self.menu.append(self.albumartItem)
        self.menu.append(self.npItem)
        self.menu.append(self.playButton)
        self.menu.append(self.previousButton)
        self.menu.append(self.nextButton)
        
        GLib.timeout_add_seconds(1,self.set_np)
        GLib.timeout_add_seconds(2,self.set_albumArt)
        GLib.timeout_add_seconds(1,self.set_icon)
        GLib.timeout_add_seconds(1,self.set_buttons)
    
        self.menu.show_all()
        
        Gtk.main()

    def set_icon(self):
        self.player = Playerctl.Player()
        self.status = self.player.get_property("status")
        if self.status == "Playing":
            self.indicator.set_icon("/usr/share/icons/Adwaita/32x32/actions/media-playback-start.png")
        elif self.status == "Paused":
            self.indicator.set_icon("/usr/share/icons/Adwaita/32x32/actions/media-playback-pause.png")
        else: 
            self.indicator.set_icon("/usr/share/icons/Adwaita/32x32/actions/media-playback-stop.png")
        return GLib.SOURCE_CONTINUE
    
    def set_albumArt(self):
        self.player = Playerctl.Player()
        thread = threading.Thread(target=self.getaa)
        thread.start()
        return GLib.SOURCE_CONTINUE
        
    def getaa(self):
        try:
            self.albumartData = urlopen(self.player.props.metadata["mpris:artUrl"])
            input_stream = Gio.MemoryInputStream.new_from_data(self.albumartData.read(), None) 
            pixbuf = Pixbuf.new_from_stream(input_stream, None)
            self.albumArt.set_from_pixbuf(pixbuf)
        except TypeError or URLError:
            self.albumArt.clear()

    def set_np(self):
        self.player = Playerctl.Player()
        self.status = self.player.get_property("status")
        try:
            self.npItem.set_label("%s\n%s\n%s" % (self.player.get_title(),self.player.get_album(),self.player.get_artist()))
        except GLib.Error:
            self.npItem.set_label("Media Control Indicator")
        return GLib.SOURCE_CONTINUE
        
    def set_buttons(self):
        self.player = Playerctl.Player()
        self.status = self.player.get_property("status")
        
        if self.status == "Playing":
            self.playButton.set_sensitive(True)
            self.nextButton.set_sensitive(True)
            self.previousButton.set_sensitive(True)
            self.playButton.set_label("Pause")
            self.playButton.set_image(image=Gtk.Image(stock=Gtk.STOCK_MEDIA_PAUSE))
        elif self.status == "Paused":
            self.playButton.set_sensitive(True)
            self.nextButton.set_sensitive(True)
            self.previousButton.set_sensitive(True)
            self.playButton.set_label("Play")
            self.playButton.set_image(image=Gtk.Image(stock=Gtk.STOCK_MEDIA_PLAY))
        else: 
            self.playButton.set_sensitive(False)
            self.nextButton.set_sensitive(False)
            self.previousButton.set_sensitive(False)
        return GLib.SOURCE_CONTINUE

        
    def mediaPlay(self, Widget):
        self.player = Playerctl.Player()
        self.player.play_pause()
        
    def mediaPrevious(self, Widget):
        self.player = Playerctl.Player()
        self.player.previous()
    def mediaNext(self, Widget):
        self.player = Playerctl.Player()
        self.player.next()
        
if __name__ == "__main__":
    imc = media_control_indicator()
    imc.main()
