# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2020/1/3 11:19


class XadminPagintor(object):
    """
    total_length:数据库数据总条数；
    amount_per_page:每页展示的条数；
    display_page:总共分成多少页；
    current_page:当前第几页
    """
    def __init__(self,total_length,amount_per_page=20,display_pages=7,current_page=1):
        self.total_length = total_length
        self.amount_per_page = amount_per_page
        self.display_pages = display_pages
        # 当前的页码应该是一个整数，为了防止用户发来的页码不是不是数字，如：“1”；
        # 或者是一堆全七八糟的字符，如：“asdfadsf”
        # 或者是一个负数，如：“-1”
        try:
            self.current_page = int(current_page)
        except Exception as e:
            self.current_page = 1
        if self.current_page <= 0:
            self.current_page = 1
        elif self.current_page > self.total_page:
            self.current_page = self.total_page

    @property
    def total_page(self):
        """
        #>>> divmod(1,2)
        #>>> (0, 1);
        #>>> divmod(3,2)
        #>>> (1, 1)
        根据a,b的值确定数据应该分成多少页，若当有余数时，因多分一页
        """
        a,b = divmod(self.total_length,self.amount_per_page)
        if b > 0:
            return a+1
        return a

    def page_num(self):
        if self.total_page <= self.display_pages: #如果计算出来的总页数小于默认的页数，则显示计算出的页数
            return range(1,self.total_page+1)

        interaval,extra = divmod(self.display_pages,2)
        if self.current_page + interaval >= self.total_page:
            return range(self.total_page-self.display_pages + 1,self.total_page +1)
        elif abs(self.current_page - interaval-1) <=0:
            return range(1,self.display_pages+1)
        if extra > 0:
            return range(self.current_page -interaval, self.current_page + interaval)
        return range(self.current_page -interaval, self.current_page + interaval + 1)

    def content_range(self):
        page = self.current_page
        start = (page-1)*self.amount_per_page
        end = page*self.amount_per_page
        return start,end