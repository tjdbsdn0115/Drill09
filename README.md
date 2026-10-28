# Drill09 - AutoRun 캐릭터 컨트롤러

이번 과제: [별도 AutoRun 상태 클래스와 실행 안내](Labs/LEC12_CharacterController/README.md)

```powershell
python -m pip install -r Labs/LEC12_CharacterController/requirements.txt
python Labs/LEC12_CharacterController/main.py
```

IDLE에서 A를 누르면 5초간 속도 2배, 크기 1.5배의 자동 무적 런을 시작합니다.
화면 양 끝에서 방향을 바꾸고, 방향키를 누르면 해당 방향의 일반 RUN으로 전환합니다.
5초가 지나면 IDLE로 복귀하며 크기와 무적 여부를 복구합니다.

![상태 다이어그램](Labs/LEC12_CharacterController/docs/state_diagram.png)

[PNG 이미지](Labs/LEC12_CharacterController/docs/state_diagram.png) ·
[SVG 원본](Labs/LEC12_CharacterController/docs/state_diagram.svg) ·
[AutoRun 클래스](Labs/LEC12_CharacterController/auto_run.py)

## 이전 과제 - 소년 상하좌우 이동 및 방향 바꾸기

과제 파일: [animation_homework.py](Labs/LEC10_HandlingInputs/animation_homework.py)

```powershell
python -m pip install pico2d
python Labs/LEC10_HandlingInputs/animation_homework.py
```

방향키로 소년을 움직입니다. 정지 시 IDLE을 재생하고, 위·아래 이동은 마지막 좌우 방향을 유지합니다.
캐릭터가 화면 밖으로 나가지 않도록 네 경계를 제한합니다. ESC 또는 창 닫기로 종료합니다.
강의의 `animation_sheet.png`와 `TUK_GROUND.png`를 사용합니다.

[조건별 구현·코드 설명·검증 결과](Labs/LEC10_HandlingInputs/README_Drill09.md)

실제 개발 변경 7개 커밋을 포함한 이력은 이 저장소의 Commits에서 확인할 수 있습니다.

제출 주소: `https://github.com/tjdbsdn0115/Drill09.git`
