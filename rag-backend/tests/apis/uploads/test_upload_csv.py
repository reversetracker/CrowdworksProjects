import uuid

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

import directories


@pytest.mark.asyncio
async def test_upload_csv(client: AsyncClient, mocker: MockerFixture) -> None:
    mocker.patch(
        target="tempfile.mktemp",
        return_value="/var/folders/tj/xw68bt0s3nl2s0b1lhpgbcyr0000gn/T/tmpetavl9dt.csv",
    )

    with open(directories.csv_file, "rb") as pdf_file:
        csv_binary = pdf_file.read()

        response = await client.post(
            "/v1/uploads/csv",
            files={
                "files": ("address.csv", csv_binary, "application/csv"),
            },
        )

        assert response.status_code == 200
        assert response.json() == [
            {
                "page_content": "John: Jack\nDoe: McGinnis\n120 jefferson st.: 220 hobo Av.\nRiverside: Phila\nNJ: PA\n08075: 09119",
                "metadata": {
                    "source": "/var/folders/tj/xw68bt0s3nl2s0b1lhpgbcyr0000gn/T/tmpetavl9dt.csv",
                    "row": 0,
                },
                "type": "Document",
            },
            {
                "page_content": 'John: John "Da Man"\nDoe: Repici\n120 jefferson st.: 120 Jefferson St.\nRiverside: Riverside\nNJ: NJ\n08075: 08075',
                "metadata": {
                    "source": "/var/folders/tj/xw68bt0s3nl2s0b1lhpgbcyr0000gn/T/tmpetavl9dt.csv",
                    "row": 1,
                },
                "type": "Document",
            },
            {
                "page_content": 'John: Stephen\nDoe: Tyler\n120 jefferson st.: 7452 Terrace "At the Plaza" road\nRiverside: SomeTown\nNJ: SD\n08075: 91234',
                "metadata": {
                    "source": "/var/folders/tj/xw68bt0s3nl2s0b1lhpgbcyr0000gn/T/tmpetavl9dt.csv",
                    "row": 2,
                },
                "type": "Document",
            },
            {
                "page_content": "John: \nDoe: Blankman\n120 jefferson st.: \nRiverside: SomeTown\nNJ: SD\n08075: 00298",
                "metadata": {
                    "source": "/var/folders/tj/xw68bt0s3nl2s0b1lhpgbcyr0000gn/T/tmpetavl9dt.csv",
                    "row": 3,
                },
                "type": "Document",
            },
            {
                "page_content": 'John: Joan "the bone", Anne\nDoe: Jet\n120 jefferson st.: 9th, at Terrace plc\nRiverside: Desert City\nNJ: CO\n08075: 00123',
                "metadata": {
                    "source": "/var/folders/tj/xw68bt0s3nl2s0b1lhpgbcyr0000gn/T/tmpetavl9dt.csv",
                    "row": 4,
                },
                "type": "Document",
            },
        ]
