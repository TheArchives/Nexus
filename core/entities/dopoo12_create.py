if self.client.username.lower().startswith("dopoo"):
    self.client.sendError("You are banned for: asking for your own entity")
elif self.client.isMod():
    self.client.sendServerMessage("Greetz to you")
else:
    self.client.sendServerMessage("huh why are you running this")