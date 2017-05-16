from models import Group
import telegram
import datetime
import dateutil.parser

TOKEN='TELEGRAM_TOKEN'

bot = telegram.Bot(token=TOKEN)
groups = Group.all()
now = datetime.datetime.now()

for group in groups:
    list_active = group.lists().opened().first()

    # Verify there are not list active
    if list_active is None:
        lists = group.lists().closed().take(10).get()

        minutes = 0
        occurrences = 0

        # Loop over the lists and check occurrences of hours
        for _list in lists:
            date = dateutil.parser.parse(str(_list.created_at))
            print "list hour {}".format(date.hour)
            print "cron hour {}".format(now.hour)

            if date.hour == now.hour:
                minutes = minutes + date.minute
                occurrences = occurrences + 1

        print "occurrences: {}".format(occurrences)
        # If there are more than 4 occurrences then verify the minutes
        if occurrences >= 4:
            mean_minutes = minutes / occurrences
            print "mean minutes: {}".format(mean_minutes)

            # The cron run every 30 minutes,
            # if the mean is between the minute 0 and 29
            # or between minute 30 and 59
            # Send a message
            if (mean_minutes > now.minute) and (mean_minutes < (now.minute + 29)):
                bot.send_message(chat_id=group.id,
                                 text="No quieren crear una lista :'v?")
