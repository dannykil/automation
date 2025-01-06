import traceback

def try_except():

    try:
        print('1st try')

        # 1) KeyError : 없는 키에 접근하려고 할 때
        # dictionary = { 'name':'jmkil', 'age':'38'}
        # print(dictionary['ages'])

        # 2) ValueError : 리스트에 없는 값에 접근하려고 할 때
        # list = ['a', 'b', 'c']
        # print(list.index('d'))

        # 3) IndexError
        # a = [1,2]
        # print(a[3])

        # 4) SyntaxError # 동작안함
        # a = 3
        # if a > 3
        #     print(a)
        # for i in range(10)
        #     print(i)

        # 5) NameError : 없는 변수를 호출했을 때
        # a = 3
        # print(b)

        # 6) ZeroDivisionError
        # 4/0

        # 7) FileNotFoundError
        # with open('./conf/config.json') as f:
        #     user_config = json.load(f)

        # 8) TypeError

        # 9) AttributeError : 잘못된 메서드나 속성을 사용했을 때
        # a = 3
        # print(a.message)
        
        # 10) ConnectionError


        # raise : exception 강제 발생(정의된 Exception이 적용됨)
        # if a < 5:
        #     print('raise')
        #     raise Exception


    except KeyError as e:
        print('KeyError')
    
    except ValueError as e:
        print('ValueError')

    except IndexError as e:
        print('IndexError')

    # except SyntaxError as e: # 동작안함
    #     print('SyntaxError')

    except NameError as e:
        print('NameError')
    
    except ZeroDivisionError as e:
        print('ZeroDivisionError')
    
    except FileNotFoundError as e:
        print('ZeroDivisionError')
    
    except TypeError as e:
        print('TypeError')

    # import traceback
    # 에러메시지 변수 저장
    except AttributeError as e: 
        print('AttributeError')
        # err_msg = traceback.format_exc()
        # print(err_msg)
    
    except ConnectionError as e:
        print('ConnectionError')
    
    except TimeoutException as e: 
        print('TimeoutException')
        print('')


    except Exception as e:
        print('1st Exception')
        # print(e)
    
    # exception없이 모두 정상적으로 실행됐을 때 else문 실행
    # * 생략 가능하나 사용 시 except문이 반드시 있어야함(없으면 오류 발생)
    else:
        print('1st else')

        # try-except-else 내 다시 try문 사용가능 x 2
        try:
            print('else - 2nd try')
        except Exception as e:
            print('else - 2nd except')
        else:
            print('else - 2nd else')

            # try-except-else 내 다시 try문 사용가능 x 3
            try:
                print('else - else - 3rd try')
            except Exception as e:
                print('else - else - 3rd except')
            else:
                print('else - else - 3rd else')

                # try-except-else 내 다시 try문 사용가능 x 4
                try:
                    print('else - else - else - 4th try')
                except Exception as e:
                    print('else - else - else - 4th except')
                else:
                    print('else - else - else - 4th else')

                    # try-except-else 내 다시 try문 사용가능 x 5
                    try:
                        print('else - else - else - 5th try')
                    except Exception as e:
                        print('else - else - else - 5th except')
                    else:
                        print('else - else - else - 5th else')
                    finally:
                        print('else - else - else - 5th finally')
                finally:
                    print('else - else - else - 4th finally')

            finally:
                print('else - else - 3rd finally')

        finally:
            print('else - 2nd finally')
    
    finally:
        print('1st finally')


try_except()

