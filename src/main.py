def extract():
    # GET API
    pass

def transform(data):
    # select/rename/clean fields
    pass

def load(data):
    # write to database
    pass

def main():
    raw = extract()
    transformed = transform(raw)
    load(transformed)

if __name__ == "__main__":
    main()