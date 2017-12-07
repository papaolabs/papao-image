# papao-image
> Milou를 위한 파이썬 기반 이미지 저장 및 분석 서버

## 개발 환경

- Python 3.5+

## 설치

papao-image를 사용하기 위해서는 requirements.txt으로 제공되는 라이브러리들을 설치해야 합니다.
쉘에서 아래 명령어를 이용하여 필요 라이브러리를 설치하세요.
```shell
$ pip3 install -r requirements.txt
```

## Quick start

papao-image를 실행하기 위해서는 아래 명령어를 쉘에서 입력하세요.
```shell
$ python3 runserver <ip>:<port>
```

#### 외부 연동 설정
papao-image에서는 이미지 분석에 사용되는 Vision API와 이미지 저장에 사용되는 AWS의 app key, 그리고 데이터베이스 연결에 필요한 설정 파일을 별도로 관리중입니다. 해당 설정은 team papao의 커미터에게 직접 전달받아 사용하실 수 있습니다.
AWS CLI와 매개변수에 키를 할당하여 연동하여야 합니다. 자세한 사항은 커미터에게 문의하세요.


## 컨트리뷰션

papao-image는 여러분들의 컨트리뷰션을 환영합니다. 지금 [Issue](https://github.com/papaolabs/papao-image/issues) 게시판에서 컨트리뷰션 가능한 내용을 확인해주세요.

## 정보

Team papao – [facebook page](https://www.facebook.com/pg/papaolabs) – ksy6808@gmail.com

[https://github.com/papaolabs](https://github.com/papaolabs/)

[license-image]: https://img.shields.io/badge/License-MIT-blue.svg
[license-url]: LICENSE
[version-image]: https://img.shields.io/badge/version-v1.0-fc4e75.svg
