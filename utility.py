class MethodMerger:
    def add_method(method):
        if self.methods == None:
            self.methods = [method]
        else:
            self.methods.append(method)

    def merged_method():
        if self.methods != None:
            for m in self.methods:
                m()

def bake_args_into_func(func,*args):
    def baked_func():
        return func(*args)
    return baked_func

