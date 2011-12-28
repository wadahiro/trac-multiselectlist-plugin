# -*- coding: utf-8 -*-

from trac.core import *
from genshi.filters.transform import Transformer
from trac.web.api import ITemplateStreamFilter
from genshi.builder import tag
from trac.config import ListOption
from trac.web.main import IRequestFilter

class MultiSelectList(Component):
    u"""カスタムフィールドにおいて、複数選択を可能にするためのプラグイン
    """
    implements(IRequestFilter,ITemplateStreamFilter)

    multilist = ListOption('multiselectlist', 'fieldname',
        doc = u"""複数選択を可能にするカスタムフィールドの名称。
        カンマ区切りで複数指定を行うことが可能です。
        （例：hogefield,fugafield）
        なお、指定した名称に対して、リスト項目を定義する必要があります。
        項目はカンマ区切りで指定します。
        （例：hogefield.values = hoge,fuga,hogehoge,fugafuga
        """)

    # iniファイルの中で定義した値をキーとしてiniファイルに指定する場合、
    # ListOptionなどで記載することはできないんだろうか・・・。
    # （IniAdminの画面からだけでは処理できなくなってしまう）
    # こういう場合は、自前で管理画面を作成する必要がある？？

    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, formdata):
        if (filename == 'ticket.html'):
            for item in self.multilist:
                values = self.env.config.get('multiselectlist', '%s.values' % item)
                if values:
                    key = 'field_%s' % unicode(item)
                    # 既存のチケットの場合はDBに格納されている値を取得する
                    inputvalues = []
                    if key in req.args:
                        # チケット登録時のバリデーションで引っかかった場合
                        # なお、DBに保管されている値より優先しなければならない
                        inputvalues = req.args.get(key)
                    elif req.path_info.startswith('/ticket'):
                        ticketno = req.path_info[8:]
                        db = self.env.get_db_cnx()
                        cursor = db.cursor()
                        sql = "select value from ticket_custom where ticket=%s and name='%s'" % (ticketno, item)
                        cursor.execute(sql)
                        row = cursor.fetchone()
                        if row:
                            inputvalues = row[0].split(',')

                    self.env.log.info(inputvalues)
                    value = values.split(',')
                    xpath = '//input[@id="field-%s"]' % item
                    # input要素をselect/option要素に置き換える。
                    # タグの繰り返しを行う場合は、配列で指定すればいいようだ。
                    stream |= Transformer(xpath).replace(
                        tag.select(
                            [tag.option(v, selected=(v in inputvalues or None)) for v in value],
                            id='field-%s' % item, name='field_%s' % item, size='4', multiple='true'))
        return stream

    # IRequestFilter
    def pre_process_request(self, req, handler):
        if req.method=='POST' and (req.path_info.startswith('/ticket') or req.path_info.startswith('/newticket')):
            # リストをそのままTicketシステムに渡すとエラーになるので、カンマ区切りのテキストに変換する。
            # なお、DBにはカンマ区切りのテキストのまま格納されることになるので、表示する際にはそれをばらす必要がある。
            # （このプラグインでは、ITemplateStreamFilterの処理としてデータを展開している）
            for item in self.multilist:
                key = 'field_%s' % unicode(item)
                if key in req.args:
                    value = req.args.get(key)
                    self.env.log.info(value)
                    newvalue = ''
                    if isinstance(value, list):
                        for v in value:
                            if newvalue != '':
                                newvalue += ','
                            newvalue += unicode(v)
                        req.args[key] = newvalue
        return handler

    def post_process_request(self, req, template, content_type):
        """No-op"""
        return (template, content_type)

    def post_process_request(self, req, template, data, content_type):
        """No-op"""
        return (template, data, content_type)
