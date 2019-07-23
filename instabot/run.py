from bot import Bot
import click


def start_like(bot, hashtags, pics, follow=False):
    print(f'Starting to LIKE users.')
    bot.log_in()
    if follow:
        bot.create_followers_list()
    bot.iterate_over_hashtags(hashtags, pics, follow)
    bot.quit()
    bot.summary()


def start_unfollow(bot, followers_number):
    print(f'Starting to UNFOLLOW users, {followers_number} to be left.')
    bot.log_in()
    bot.clear_followers(followers_number)
    bot.quit()


@click.command()
@click.argument('username')
@click.argument('password')
@click.option('--unfollow', is_flag=True, help='Unfollow flag, use --leave to set nr of followers to leave.')
@click.option('--leave', default=600, help='Leave <int> followers, default=600')
@click.option('--follow', is_flag=True, help='Follow flag.')
@click.option('--hashtags', default=10, help='No of hashtags to iterate over')
@click.option('--pics', default=100, help='No of hashtags pics to iterate over')
@click.option('--chrome', help='Full path to chromedriver file')
@click.option('--tags', help='Full path to hashtags .csv file')
def run(username, password, unfollow, follow, leave, hashtags, pics, chrome, tags):
    bot = Bot(username, password, chrome, tags)
    if unfollow:
        start_unfollow(bot, leave)
    else:
        start_like(bot, hashtags, pics, follow)


if __name__ == '__main__':
    run()
