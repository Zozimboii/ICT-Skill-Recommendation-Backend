import asyncio

from prisma import Prisma


async def main() -> None:
    db = Prisma()
    await db.connect()

    # สร้าง User Admin เหมือนในตัวอย่าง JS
    await db.user.upsert(
        where={"username": "admin"},
        data={
            "create": {
                "username": "admin",
                "email": "admin@gmail.com",
                "password": "12345678",
            },
            "update": {},
        },
    )

    # ถ้ามีตารางอื่นๆ เช่น Category ก็ใส่เพิ่มตรงนี้ได้
    print("✅ Seed ข้อมูล Admin และค่าตั้งต้นเรียบร้อย!")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
