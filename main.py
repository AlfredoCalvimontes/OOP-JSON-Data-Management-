from interface import main_menu, welcome
from data_management import dataLoading


def main():
    '''Calls tha main initializing functions.'''
    try:
        dataLoading()
        welcome()
        main_menu()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
