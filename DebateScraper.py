import scrapy
import os

class BaseDebateSpider(scrapy.Spider):
    name = None
    debate_type = None

    def start_requests(self):
        yield scrapy.Request(url=f"https://www.oireachtas.ie/en/debates/find/?debateType={self.debate_type}", callback=self.parse_initial_page)

    def parse_initial_page(self, response):
        last_debate_page_url = response.css("div.debate-result-item:first-child h3 a::attr(href)").get()
        yield scrapy.Request(url=last_debate_page_url, callback=self.parse_last_debate_page)

    def parse_last_debate_page(self, response):
        speeches = response.css('div.speech')

        for speech in speeches:
            speaker_name = speech.css('div.c-avatar__name-link::text').get()
            speech_text = ' '.join(speech.css('div.content > p::text').getall())
            speech_date = speech.css('div.date::text').get()

            # Create a directory for each speaker if it doesn't exist
            speaker_directory = f'speakers/{speaker_name}'
            os.makedirs(speaker_directory, exist_ok=True)

            # Create or open the speaker's file to append the speech
            file_path = f'{speaker_directory}/{speaker_name}.json'
            with open(file_path, 'a+') as f:
                f.write(f'{{"speech_date": "{speech_date}", "speech_text": "{speech_text}"}}\n')

        # Continue to the previous debate page if available
        previous_debate_page_url = response.css("li.previous a::attr(href)").get()
        if previous_debate_page_url:
            yield scrapy.Request(url=previous_debate_page_url, callback=self.parse_last_debate_page)

class DailDebateSpider(BaseDebateSpider):
    name = "daildebatespider"
    debate_type = "dail"

class SeanadDebateSpider(BaseDebateSpider):
    name = "seanaddebatespider"
    debate_type = "seanad"

class CommitteeDebateSpider(BaseDebateSpider):
    name = "committeedebatespider"
    debate_type = "committee"
