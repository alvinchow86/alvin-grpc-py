from setuptools import setup

# get version
__version__ = None
exec(open('alvinchow/grpc/version.py').read())

setup(
    name='alvinchow-grpc-lib',
    version=__version__,
    description="gRPC Python library",
    packages=[
        'alvinchow/grpc',
        'alvinchow/grpc/client',
        'alvinchow/grpc/protobuf',
        'alvinchow/grpc/server',
        'alvinchow/grpc/test',
    ],
    package_data={},
    scripts=[],
    install_requires=[
        'python-dateutil>=2.7',
        'protobuf>=3.6.0',
        'alvin-python-lib>=0.0.1',
        'grpcio-status>=1.20',
        'protobuf-serialization>=0.1.1',
    ]
)
