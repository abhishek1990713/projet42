import scrapy


class Sample3Spider(scrapy.Spider):
    name = 'sample3'

    page_number = 2
    allowed_domains = ['www.amazon.in']
    start_urls = [
        'https://www.amazon.in/s?k=face+wash&page=1&crid=14PFVH30EJSEY&qid=1674114383&sprefix=face+wash%2Caps%2C324&ref=sr_pg_2']

    def parse(self, response):
        for tree in response.xpath(
                '//div[@class="a-section a-spacing-small puis-padding-left-small puis-padding-right-small"]'):
            title = tree.xpath(".//div/h2/a/span/text()").get()

            star = tree.xpath(
                './/div[@class="a-section a-spacing-none a-spacing-top-micro"]/div/span/span/a/i/span/text()').get()

            discount = tree.xpath(
                './/div[@class="a-section a-spacing-none a-spacing-top-small s-price-instructions-style"]/div[@class="a-row a-size-base a-color-base"]/span/text()').get()


            link = tree.xpath('.//div/h2/a/@href').get()
            url = f"https://www.amazon.in/{link}"
            absolute_url= response.urljoin(link)

            yield response.follow(url=absolute_url ,callback=self.page2parse , meta= {'Title' : title , 'Star':star , 'Discount': discount, 'URL':url})

    def page2parse(self,response):

        title = response.request.meta['Title']
        star = response.request.meta['Star']
        discount = response.request.meta['Discount']
        PRODUCT_URL = response.request.meta['URL']
        #title = response.xpath('//span[@id ="productTitle"]/text()').get()
        price = response.xpath('//div[@class="a-section a-spacing-none aok-align-center"]/span/span/text()').get()

        #discount = response.xpath('//div[@class="a-section a-spacing-none aok-align-center"]/span/text()').get()
        original_price = response.xpath('//div[@class="a-section a-spacing-small aok-align-center"]/span/span/span/span/text()').get()
        review_one = response.xpath('//div[@class ="a-section review aok-relative"][1]/div/div/div[@class ="a-row a-spacing-small review-data" ]/span/div/div/span/text()').get()
        review_two = response.xpath('//div[@class ="a-section review aok-relative"][2]/div/div/div[@class ="a-row a-spacing-small review-data" ]/span/div/div/span/text()').get()
        review_three = response.xpath('//div[@class ="a-section review aok-relative"][3]/div/div/div[@class ="a-row a-spacing-small review-data" ]/span/div/div/span/text()').get()
        review_four = response.xpath('//div[@class ="a-section review aok-relative"][4]/div/div/div[@class ="a-row a-spacing-small review-data" ]/span/div/div/span/text()').get()
        review_five = response.xpath('//div[@class ="a-section review aok-relative"][5]/div/div/div[@class ="a-row a-spacing-small review-data" ]/span/div/div/span/text()').get()
        yield {
            'PRODUCT_URL':PRODUCT_URL,
            'title':title,
            'star':star,
            'price':price,
            'discount':discount,
            'original_price':original_price,
            'review_one':review_one,
            'review_two':review_two,
            'review_three':review_three,
            'review_four':review_four,
            'review_five':review_five
        }
        next_page = 'https://www.amazon.in/s?k=face+wash&page=' + str(
            Sample3Spider.page_number) + '&crid=14PFVH30EJSEY&qid=1674114383&sprefix=face+wash%2Caps%2C324&ref=sr_pg_2'
        # next_page = 'https://www.amazon.in/s?k=organic+soaps&page=' + str( FacewashSpider.page_number) + '&crid=OKP6X5GJP4TZ&qid=1653651197&sprefix=organic+soaps%2Caps%2C717&ref=sr_pg_2'
        if Sample3Spider.page_number < 7:
            Sample3Spider.page_number += 1
            yield response.follow(next_page, callback=self.parse)

