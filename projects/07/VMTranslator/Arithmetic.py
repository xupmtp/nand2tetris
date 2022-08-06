class Arithmetic:
    fn = {}
    fn['add'] = lambda x, y: x + y
    fn['sub'] = lambda x, y: x - y
    fn['neg'] = lambda y: -y
    fn['eq'] = lambda x, y: x == y
    fn['gt'] = lambda x, y: x > y
    fn['lt'] = lambda x, y: x < y
    fn['and'] = lambda x, y: x and y
    fn['or'] = lambda x, y: x or y
    fn['not'] = lambda y: not y
