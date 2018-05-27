#!/usr/bin/env python3

"""
FeedScrapy is software that collect specifics news from a feed and
send it to an e-mail (or email list).
author: Clederson Cruz
Year: 2018
License: GNU GENERAL PUBLIC LICENSE (GPL)
"""

import os
import re
import json
from feeds import feedscrapy, feedmail
from time import sleep

MAXFEED = 3
CLOCK = 30
TEMPLATE_NAME = 'basic.html'
TYPE_SEARCH = 0
MAXLOG_LENGTH = 500


def generic_read_item(path):
    """
    Read some file and returns a list of the found content.
    :param path: some path
    :return: list of the found content
    """
    items = []

    try:
        file = open(path, 'r')
    except FileNotFoundError:
        generic_write_message(path)
        exit(0)

    for line in file:
        items.append(line.lower().strip())

    file.close()
    return items


def generic_write_message(path):
    """
    Used by generic functions to write messages.
    :param path: path to write the message
    :return:
    """
    print('Arquivo "%s" não encontrado.' % os.path.basename(path))
    print('Criando arquivo...')
    generic_write_item(path, '<<Insira um item por linha>>')
    print('Arquivo criado.')


def generic_write_item(path, content):
    """
    Write some file with some content.
    :param path: some path
    :param content: some content
    :return: None
    """
    file_name = os.path.basename(path)
    dir_path = os.path.dirname(path)

    try:
        try:
            os.makedirs(dir_path)
        except FileExistsError:
            pass

        with open(path, 'w') as file:
            file.write(content)
            file.close()

    except PermissionError:
        print(f'Problema ao escrever no arquivo "{file_name}", permissão negada.')
        exit(0)


def load_template():
    """
    Load the chosen template to be used in a Email.
    :return: None
    """
    try:
        path = os.path.join('templates', TEMPLATE_NAME)
        with open(path, 'r') as template:
            content = template.read()
            template.close()
    except FileNotFoundError:
        print('Template %s não encontrado.' % os.path.basename(path))
        exit(0)

    return content


def write_output(entries):
    """
    Write a content in an output file with a template chosen.
    :param entries: news to be inserted on template.
    :return: None
    """
    try:
        path = 'output'
        if not os.path.exists(path):
            os.makedirs(path)

        file_name = os.path.join(path, 'content.html')
        file = open(file_name, 'w')
    except PermissionError:
        print(f'Problema ao escrever no arquivo "{file_name}", permissão negada.')
        exit(0)

    f_entries = ''
    for item in entries:
        f_entries = f_entries + item + '<br>'

    content = load_template().replace('{{f_entries}}', f_entries)

    file.write(content)
    file.close()


def generic_read_content(path):
    """
        Like generic_load_item, but this returns the content only without a list.
        :param path: some path
        :return: content of the read file
        """
    try:
        if not os.path.exists(path):
            raise Exception(f"Not found path '{path}'")

        file = open(path, 'r')
        content = file.read()
        file.close()
    except PermissionError:
        print('Problema ao ler o arquivo "%s", permissão negada.' % os.path.basename(path))
        exit(0)

    return content


def create_server(path_config):
    """
    Used to create a SMTPServer to send an Email.
    :param path_config: path of the config file
    :return: a SMTPServer
    """
    try:
        with open(path_config, 'rb') as config_file:
            data = json.load(config_file)
            config_file.close()
    except FileNotFoundError:
        print(f'Arquivo {path_config} não encontrado')
        exit()

    server = feedmail.SMTPServer(
        data['server'],
        data['port'],
        data['user'],
        data['password']
    )

    return server


def control_log():
    """
    For many reasons the log file should not be larger than a X limit.
    This function control the log file length.
    :return:
    """
    log_path = os.path.join('log', 'last_feed.log')
    cur_length_log = os.path.getsize(log_path)/10E6  # 1 MB

    if cur_length_log > MAXLOG_LENGTH:
        generic_write_item(log_path, '')


def filter_entries(entries):
    """
    Filter the entries in a log, avoiding redundancy of sending.
    :param entries: the news to be sent
    :return: filtered news
    """
    path = os.path.join('log', 'last_feed.log')
    if not os.path.exists(path):
        titles = ''
        # List to String
        for entry in entries:
            title = re.search(r'<h1>(.*)</h1>', entry).group(0)
            titles = titles + title + '\n'
        generic_write_item(path, titles)
        control_log()

        return entries
    else:
        log = generic_read_item(path)
        f_entries = []

        for entry in entries:
            title = re.search(r'<h1>(.*)</h1>', entry).group(0).strip().lower()

            if title not in log:
                f_entries.append(entry)

        with open(path, 'a') as log_file:
            # List to String
            titles = ''
            for entry in f_entries:
                title = re.search(r'<h1>(.*)</h1>', entry).group(0)
                titles = titles + title + '\n'

            log_file.write(titles)
            log_file.close()
            control_log()

        return f_entries


def app_config():
    """
    The main configurations are loaded here from the app_config.json.
    :return: None
    """
    path_config = os.path.join('config', 'app_config.json')
    data = {}
    try:
        with open(path_config, 'rb') as config_file:
            data = json.load(config_file)
            config_file.close()
    except FileNotFoundError:
        print(f'Arquivo {path_config} não encontrado')
        exit()

    global MAXFEED, CLOCK, TEMPLATE_NAME, TYPE_SEARCH, MAXLOG_LENGTH
    MAXFEED = data['maxfeed']
    CLOCK = data['clock']
    TEMPLATE_NAME = data['template_name']
    TYPE_SEARCH = data['type_search']
    MAXLOG_LENGTH = data['maxlog_length']


def main():
    # Checking
    print('[INFO]\tInicializando...')
    feeds_path = os.path.join('input', 'feeds.txt')
    feeds = generic_read_item(feeds_path)
    if len(feeds) == 0:
        print('Nenhum feed encontrado em "%s"' % os.path.basename(feeds_path))
        exit(0)
    print('[OK]\tEncontrado', os.path.basename(feeds_path))

    keyword_list_path = os.path.join('input', 'keyword_list.txt')
    keyword_list = generic_read_item(keyword_list_path)
    if len(keyword_list) == 0:
        print('[ERR]\tNenhuma palavra-chave encontrada em "%s"' % os.path.basename(keyword_list_path))
        exit(0)
    print('[OK]\tEncontrado', os.path.basename(keyword_list_path))

    print('[INFO]\tLendo configuração do servidor SMTP...')
    path_config = os.path.join('config', 'config_server.json')
    server = create_server(path_config)
    print('[OK]\tEncontrado configurações em', os.path.basename(path_config))

    print('[INFO]\tLendo lista de e-mails')
    emails_path = os.path.join('input', 'emails.txt')
    email_list = generic_read_item(emails_path)
    if len(email_list) == 0:
        print('Nenhum e-mail encontrado em "%s"' % os.path.basename(emails_path))
    print('[OK]\tEncontrado e-mails em', os.path.basename(emails_path))

    # Starting
    app_config()

    # Infinity loop
    while True:
        feeder = feedscrapy.Feeder(MAXFEED)
        entries = []

        for feed in feeds:
            feeder.set_rss(feed)
            tmp_entries = feeder.get_entries(keyword_list, TYPE_SEARCH)
            for entry in tmp_entries:
                entries.append(entry)

        f_entry = filter_entries(entries)
        if len(f_entry) > 0:
            print('[INFO]\tGerando saída...')
            write_output(f_entry)

            print('[INFO]\tEnviando email(s)...')
            fd_email = feedmail.Email()
            fd_email.set_addr_from(server.user)
            fd_email.set_subject('Feedscrapy - Últimas notícias')
            content_path = os.path.join('output', 'content.html')
            fd_email.attach_content(generic_read_content(content_path))

            for email in email_list:
                fd_email.set_addr_to(email)
                server.send(fd_email)

            print('[INFO]\tE-mail(s) enviado(s) com sucesso.')

        print('[INFO]\tAguardando por novas atualizações.')
        sleep(CLOCK * 60)


if __name__ == '__main__':
    main()
