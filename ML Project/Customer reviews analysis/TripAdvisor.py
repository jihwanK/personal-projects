from selenium import webdriver
import time
import csv

preUrl = 'https://www.tripadvisor.com/Restaurant_Review'
country_name = ''
prefixOfFileName = time.strftime("%Y%m%d%H%M%S", time.localtime())
fileName = 'RESULT_SINGAPORE_' + prefixOfFileName + '.csv'


# Make the preURL complete to be full URL
# Argument: information, 2-D LIST [[numOfStar, postFixUrl, nameOfRestaurant], [numOfStar, ...], ...]
# Return type: none
def completeURL(information):
    driver = webdriver.PhantomJS('/Users/jhwan/Downloads/phantomjs/bin/phantomjs')

    print('----------completeURL is called----------')

    for postfix in information:
        URL = preUrl+postfix[0]+postfix[1]

        driver.get(URL)

        labelEng =''

        try:
            labelEng = driver.find_element_by_css_selector("[for='taplc_prodp13n_hr_sur_review_filter_controls_0_filterLang_en']")
            print('no exception occured')
        except:
            continue

        strNum = labelEng.find_element_by_css_selector('span')

        if len(strNum.text[1:-1]) > 4:
            numOfEng = int(strNum.text[1]+strNum.text[3:-1])
        else: numOfEng = int(strNum.text[1:-1])

        printTheNameOfRestaurant(driver, numOfEng)
        if numOfEng == 0:
            continue

        numOfPages = calculateNumOfPages(numOfEng)

        collectReviews(driver, URL)

        for i in range(1, numOfPages):
            infixPage = 10*i
            infix = '-or' + str(infixPage)
            URL = preUrl+postfix[0]+infix+postfix[1]

            driver.get(URL)
            collectReviews(driver, URL)

    print('----------completeURL finished----------')
    driver.quit()

# Print the name of the restaurant on the 'TripAdvisor.com'
# Argument: web driver especially phantomjs, the number of English reviews, WEBDRIVER, INTEGER
# Return type: none
def printTheNameOfRestaurant(driver, numOfEng):
    h1s = driver.find_elements_by_tag_name('h1')
    for h1 in h1s:
        if h1.get_attribute('id') == 'HEADING':
            nameOfRestaurant = h1.text
            print('RESTAURANT NAME : ' + nameOfRestaurant + ' (' + str(numOfEng) + ')')
            writeNameToFile(fileName, nameOfRestaurant)
            break


# Calculate the number of pages of reviews by using total number of reviews
# Argument: the number of reviews, INTEGER
# Return type: number of pages, INTEGER
def calculateNumOfPages(numOfReviews):
    print('----------calculateNumOfPages is called----------')
    if int(numOfReviews/10) > 0:
        if numOfReviews%10 == 0:
            numOfPages = int(numOfReviews/10)
        else:
            numOfPages = int(numOfReviews/10) + 1
    elif int(numOfReviews/10) == 0:
        if numOfReviews%10 == 0:
            numOfPages = 0
        else:
            numOfPages = 1

    print('----------calculateNumOfPages finished----------')
    return numOfPages


# Collect the reviews from 'TripAdvisor.com'
# Argument: URL for collecting reviews and ratings, STRING
# Return type: none
def collectReviews(driver, URL):
    print('----------collectReviews is called----------')

    rating = []
    dates = []
    locations = []

    try:
        parentOfMore = driver.find_element_by_class_name('partnerRvw')
        more = parentOfMore.find_element_by_class_name('taLnk')
        more.click()
        time.sleep(1)

    except:
        print('there are no MORE reviews')

    finally:
        # get the reviews
        reviews = driver.find_elements_by_class_name('entry')
        reviews = getRidOfEmpty(reviews)

        # get the ratings
        basicReview = driver.find_elements_by_class_name('basic_review')
        print("---------------start------------ : " + str(len(basicReview)))
        print("URL : " + URL)


        rating = getRating(driver)
        ratings = analyzeRating(rating)
        print(ratings)

        locations = getMemberLocationInfo(driver)
        dates = getDateOfReviews(driver)

        # put the data into file
        print('**************************************** START PRINT ****************************************')
        print('size: ', str(len(reviews)), str(len(ratings)), str(len(locations)), str(len(dates)))
        writeReviewsToFile(fileName, reviews, ratings, locations, dates)
        print('**************************************** END PRINT ****************************************')

        print('----------collectReviews finished----------')


def getRating(driver):
    result = []
    basicReviews = driver.find_elements_by_class_name('basic_review')

    for inner in basicReviews:
        ratingClass = inner.find_element_by_class_name('ui_bubble_rating')
        result.append(ratingClass.get_attribute('alt'))
    return result

# Get the date when the reviews were posted
# Argument:
# Return type: result, LIST
def getDateOfReviews(driver):
    result = []
    basics = driver.find_elements_by_class_name('inlineReviewUpdate')

    for inner in basics:
        if inner.text == '': continue
        col = inner.find_element_by_class_name('col2of2')
        date = col.find_element_by_class_name('ratingDate')
        realDate = ''
        if 'ago' in date.text or 'yesterday' in date.text or 'today' in date.text:
            realDate = date.get_attribute('title')
            result.append(convertIntoOtherForm(realDate))
        else:
            realDate = date.text[9:]
            result.append(convertIntoOtherForm(realDate))
    return result


def convertIntoOtherForm(realDate):
    result = ''
    splitedDate = realDate.split(' ')
    if splitedDate[0] == 'January': splitedDate[0] = '01'
    elif splitedDate[0] == 'February': splitedDate[0] = '02'
    elif splitedDate[0] == 'March': splitedDate[0] = '03'
    elif splitedDate[0] == 'April': splitedDate[0] = '04'
    elif splitedDate[0] == 'May': splitedDate[0] = '05'
    elif splitedDate[0] == 'June': splitedDate[0] = '06'
    elif splitedDate[0] == 'July': splitedDate[0] = '07'
    elif splitedDate[0] == 'August': splitedDate[0] = '08'
    elif splitedDate[0] == 'September': splitedDate[0] = '09'
    elif splitedDate[0] == 'October': splitedDate[0] = '10'
    elif splitedDate[0] == 'November': splitedDate[0] = '11'
    elif splitedDate[0] == 'December': splitedDate[0] = '12'

    for s in splitedDate[1]:
        if s == ',': break
        result = result+s
    splitedDate[1] = result

    if len(splitedDate[1]) == 1:
        splitedDate[1] = '0'+splitedDate[1]
    #print('DATE is '+splitedDate[2]+splitedDate[0]+splitedDate[1])

    return splitedDate[2]+splitedDate[0]+splitedDate[1]



def organizeReviews(date, country):
    res = []

    if country == 'korea':
        filename = 'korea_'+prefixOfFileName+'.csv'
        flag = 20161107
    elif country == 'result_shanghai':
        filename = 'shanghai_'+prefixOfFileName+'.csv'
        flag = 20160921
    elif country == 'result_singapore':
        filename = 'singapore_'+prefixOfFileName+'.csv'
        flag = 20160721

    if int(date) >= flag:
        res.append('after')
        writeReviewsToFile(filename, res)
    else:
        res.append('before')
        writeReviewsToFile(filename, res)

    return res




# Get the country information from each reviews
# Argument: driver
# Return type: result, LIST
def getMemberLocationInfo(driver):
    result = []
    basics = driver.find_elements_by_class_name('inlineReviewUpdate')

    for inner in basics:
        if inner.text == '': continue
        #col = inner.find_element_by_class_name('col1of2')
        #memberInfo = inner.find_element_by_class_name('member_info')
        try:
            locationClass = inner.find_element_by_class_name('location')
            location = locationClass.text
            result.append(location)
        except:
            result.append('')

    return result


# Get rid of the empty elements in the list of reviews
def getRidOfEmpty(review):
    result = []
    for e in review:
        if e.text != '':
            result.append(e.text)
    return result

# Convert the crawled rating into useful data
# Argument: rating , LIST
# Return: rating, LIST
def analyzeRating(rating):
    print('----------analyzeRating is called----------')

    result = []
    #i = 0
    for e in rating:
        if e == '1.0 of 5 bubbles':
            result.append('1')
        elif e == '2.0 of 5 bubbles':
            result.append('2')
        elif e == '3.0 of 5 bubbles':
            result.append('3')
        elif e == '4.0 of 5 bubbles':
            result.append('4')
        elif e == '5.0 of 5 bubbles':
            result.append('5')
        elif e == '1.5 of 5 bubbles':
            result.append('1.5')
        elif e == '2.5 of 5 bubbles':
            result.append('2.5')
        elif e == '3.5 of 5 bubbles':
            result.append('3.5')
        elif e == '4.5 of 5 bubbles':
            result.append('4.5')

    print('----------analyzeRating finished----------')

    return result


# Read the postfix of URL file from desktop
# Argument: country one of (South Korea, Singapore, Shanghai), STRING
# Return type: information of restaurant, 2-D LIST [[numOfStar, postfixUrl, nameOfRestaurant], [numOfStar, ...], ...]
def readPostfixFromFile(country):
    print('----------readPostifxFormFile called----------')

    result = []
    with open(country, 'r') as csvFile:
        information = csv.reader(csvFile)
        for row in information:
            inner = []
            inner.append(row[2])
            inner.append(row[3])
            result.append(inner)
        print('----------readPostifxFormFile finished----------')
    return result


# Write the reviews, ratings and the others to csv file
# Argument: file_name, reviews, ratings, STRING, LIST, LIST
# Return type: none
def writeReviewsToFile(fileName, reviews, ratings, locations, dates):
    with open(fileName, 'a') as csvFile:
        csvWriter = csv.writer(csvFile)
        idx = 0
        while True:
            if idx == len(dates): break
            csvWriter.writerow([reviews[idx], ratings[idx], locations[idx], dates[idx]])
            idx += 1


def writeNameToFile(fileName, restaurant):
    with open(fileName, 'a') as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(['RESTAURANT', restaurant])
