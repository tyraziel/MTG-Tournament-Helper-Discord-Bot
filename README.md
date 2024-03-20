# MTG-Tournament-Helper-Discord-Bot

Bot to help with the management of swiss style tournaments, where deck lists will be validated against (for legality at submission time) and posted to Moxfield.

This bot has been programmed to hit the Moxfield.com API at various commands or interactions.  The Moxfield API is not a publicly facing API and permission is required to make use of it https://www.moxfield.com/help/faq#moxfield-api.  This specific program will be (has been) coded to be rate-limited against Moxfield's API such that there is no more than approximetly one (1) request from it per second.

Use of this code that hits the Moxfield API or knowledge of the Moxfield API from viewing this code and executing against Moxfield's API is AT YOUR OWN RISK.

### MIT License

Copyright (c) 2024 tyraziel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
