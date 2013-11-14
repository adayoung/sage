from sage import prompt, ansi, player


class CustomPromptRenderer(prompt.PromptRenderer):
    """ Override prompt.PromptRenderer """

    def colorize_vital(self, value):
        """ Give us green, yellow, and red colored numbers for vitals depending on our
        percentage. """

        if value >= 66:
            return ansi.green(str(value))
        elif value >= 33:
            return ansi.bold_yellow(str(value))
        else:
            return ansi.bold_red(str(value))

    def render_balance(self):
        """ Color balances with a green/red background. """

        if 'e' in self.stats and 'x' in self.stats:
            return ansi.strfcolor("%W&gex%0")

        statout = "%W&r"

        if 'e' in self.stats:
            statout += 'e'
        else:
            statout += ' '

        if 'x' in self.stats:
            statout += 'x'
        else:
            statout += ' '

        return ansi.strfcolor(statout + "%0")

    def render_stats(self):
        """ Take balance and equilibrium out of the stats line. """
        return ''.join([c for c in self.stats if c not in ('e', 'x')])

    def render(self):
        """ The overrided render() method for the PromptRenderer class. """

        data = {
            'health': self.colorize_vital(player.health.percentage),
            'mana': self.colorize_vital(player.mana.percentage),
            'willpower': self.colorize_vital(player.willpower.percentage),
            'endurance': self.colorize_vital(player.endurance.percentage),
            'balance': self.render_balance(),
            'stats': self.render_stats()
        }

        fstr = "%-[{health}%-%]h [{mana}%-%]m {willpower}%-%%w {endurance}%-%e {balance}|{stats}%0-"

        return ansi.strfcolor(fstr).format(**data)


# set prompt.renderer to the instance of your own Prompt
prompt.renderer = CustomPromptRenderer()