from ethecycle.util.string_helper import strip_and_set_empty_string_to_none, extract_wallet_name

FB_TEST_URL = 'https://free.facebook.com/charissejoy.biag.5?ref_component=mfreebasic_home_header&ref_page=MMessagingThreadlistController&refid=11&ref=dbl'
FB_TEST_URL2 = 'mobile.facebook.com/ziozaveiro?fref=nf&refid=52&_ft_=mf_story_key.2282576311834504%3Atop_level_post_id.2282576311834504%3Atl_objid.2282576311834504%3Acontent_owner_id_new.100002464717344%3Aoriginal_content_id.1188557304660103%3Aoriginal_content_owner_id.579850265530813%3Athrowback_story_fbid.2282576311834504%3Apage_id.579850265530813%3Aphoto_id.1188557064660127%3Astory_location.4%3Aattached_story_attachment_style.photo%3Apage_insights.%7B%22579850265530813%22%3A%7B%22page_id%22%3A579850265530813%2C%22role%22%3A1%2C%22actor_id%22%3A100002464717344%2C%22psn%22%3A%22EntStatusCreationStory%22%2C%22attached_story%22%3A%7B%22role%22%3A1%2C%22page_id%22%3A579850265530813%2C%22post_context%22%3A%7B%22story_fbid%22%3A1188557304660103%2C%22publish_time%22%3A1556275641%2C%22story_name%22%3A%22EntStatusCreationStory%22%2C%22object_fbtype%22%3A266%7D%2C%22actor_id%22%3A579850265530813%2C%22psn%22%3A%22EntStatusCreationStory%22%2C%22sl%22%3A4%2C%22dm%22%3A%7B%22isShare%22%3A0%2C%22originalPo'
FB_PHP_URL = 'mobile.facebook.com/profile.php?lst=100006487255646%3A100004289778806%3A1497854927&id=100004289778806&fref=nf&pn_ref=story&refid=17&__tn__=C'

def test_strip_and_set_empty_string_to_none():
    assert strip_and_set_empty_string_to_none('   w ') == 'w'
    assert strip_and_set_empty_string_to_none('     ') is None
    assert strip_and_set_empty_string_to_none(5.5) == 5.5
    assert strip_and_set_empty_string_to_none('   WWW ') == 'WWW'
    assert strip_and_set_empty_string_to_none('   WWW ', to_lowercase=True) == 'www'


def test_extract_wallet_name():
    #assert extract_wallet_name(FB_TEST_URL) == 'free.facebook.com/charissejoy.biag.5'
    #assert extract_wallet_name(FB_TEST_URL2) == 'facebook.com/ziozaveiro'
    assert extract_wallet_name(FB_PHP_URL) == 'facebook.com/profile.php?id=100004289778806'
    assert extract_wallet_name(5.5) == '5.5'
    assert extract_wallet_name('https://www.woof.com/woofer') == 'woof.com/woofer'
    assert extract_wallet_name('https://www.woof.com/woofer?buddy_system=true') == 'woof.com/woofer?buddy_system=true'
