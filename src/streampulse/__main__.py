import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: streampulse <command> [options]")
        print("\nCommands:")
        print("  produce     Generate and produce events to Kafka")
        print("  consume     Consume and process events from Kafka")
        print("  serve       Start the REST API server")
        print("  init-clickhouse  Initialize ClickHouse tables")
        print("\nRun 'streampulse <command> --help' for details.")
        return 1

    command = sys.argv[1]

    if command == "produce":
        from streampulse.cli.produce import run
        return run(sys.argv[2:])
    elif command == "consume":
        from streampulse.cli.consume import run
        return run(sys.argv[2:])
    elif command == "serve":
        from streampulse.cli.serve import run
        return run(sys.argv[2:])
    elif command == "init-clickhouse":
        from streampulse.cli.init_clickhouse import run
        return run()
    else:
        print(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
