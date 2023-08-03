from flask import request

def authenticate():
  pass

def authorize(func):
  def innerasdf():
    print("I got decorated")
    func()
  return innerasdf


def login_required(func):
  def inner(self):
    print(request)
    print("I got decorated")
    return func(self)
  return inner
